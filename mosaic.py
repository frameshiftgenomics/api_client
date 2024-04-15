"""
This Mosaic API client is designed to support two workflows:

    (1) Python interpreter/script (preferred).
            
            from mosaic import Mosaic, Project

        create a mosaic instance:

            mosaic = Mosaic()

        and possibly get a specific project:

            project = mosaic.get_project(project_id)

        and work with the CRUD methods defined on those interactively. 


    (2) Command line (via Python Fire):
        
            python mosaic.py mosaic --host-type=<type> <command>

        or
            
            python mosaic.py project --mosaic-host-type=<type> --project-id=<id> <command>


    
    API tokens must be supplied in <host-type>.ini files, in the same directory.

    If there is an API call that is not supported, add it as a method to the Mosaic 
    or Project class, whichever is appropriate. See the existing methods for examples
    of how to call the underlying HTTP methods.

"""

import configparser
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import json
import sys
from requests.exceptions import HTTPError

# Suppress only the InsecureRequestWarning caused by using verify=False
# (which we use for the local Mosaic instance)
# Note: Not needed with new infrastructure.
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class Store(object):
    def __init__(self, config_file='local.ini'):
        self._config_file = config_file
        self._config = configparser.ConfigParser()
        self._config.read(config_file)

    def _write_config(self):
        with open(self._config_file, 'w') as configfile:
            self._config.write(configfile)

    def get(self, section, key):
        return self._config.get(section, key)

    def set(self, section, key, val):
        self._config.set(section, key, val)
        self._write_config()


class Mosaic(object):
    def __init__(self, host_type='local', config_file=None, show_traceback=False):
        # config_file takes precedence over host_type
        if config_file:
            store = Store(config_file)
            self._host_type = 'config_file'
        else:
            store = Store(host_type + '.ini')
            self._host_type = host_type


        self._store = store

        config_section = 'Configuration'

        self._verify = (host_type != 'local')

        if self._host_type == 'local':
            self._api_host = 'http://localhost:3000/api/v1'
        elif self._host_type == 'remote':
            self._api_host = 'https://mosaic.frameshift.io/api/v1'
        else:
            self._api_host = store.get(config_section, 'host')

        token = store.get(config_section, 'token')

        self._headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}'
        }

        self._request_history = []

        if not show_traceback:
            sys.tracebacklimit = 0

    def __repr__(self):
        return f"Mosaic('{self._host_type}')"


    def _log_request(self, req):
        """
        req is a PreparedRequest object that the 
        response object has in res.request.
        """
        req_str = f"curl -X {req.method} '{req.url}' "

        for header, value in req.headers.items():
            req_str += f" -H '{header}: {value}' "

        if req.body:
            req_str += f" -d '{req.body}' "

        self._request_history.append(req_str)


    """
    Mosaic Configuration methods
    (to avoid needing to work directly with Store() )
    """
    def get_config(self, section, key):
        self._store.get(section, key)


    def set_config(self, section, key, value):
        self._store.set(section, key, value)


    def config_file(self):
        return self._store._config_file


    """
    Mosaic HTTP request methods.
    """
    def _http_request(self, method, resource, *, params=None, data=None, file_upload=None):
        kwargs = {
                'headers': self._headers, 
                'verify': self._verify, 
                'params': params
                }

        if file_upload:
            # setting Content-Type to None lets
            # requests generate the header correctly
            # from the 'files' dict
            kwargs['headers']['Content-Type'] = None

            kwargs['files'] = {
                'file': open(file_upload, "rb")
                }

            if data:
                # if Content-Type set in this way,
                # we don't the json.dumps as below.
                kwargs['data'] = data
        elif data:
            # json.dumps prevents form encoding
            kwargs['data'] = json.dumps(data)

        url = f'{self._api_host}/{resource}'

        res = method(url, **kwargs)

        self._log_request(res.request)

        # Try to return an error message if one exists.
        err_msg = None
        try:
            res.raise_for_status()
        except:
            try:
                obj = res.json()
                err_msg = f"\n\nHTTP {res.status_code}\n{url}\n{obj['message']}"
            except json.JSONDecodeError:
                err_msg = f'\n\nHTTP {res.status_code}\n{url}\n(No message sent)'
        if err_msg:
            raise HTTPError(err_msg)

        try:
            return res.json()
        except json.JSONDecodeError:
            # the server might not have returned anything.
            return None


    def get(self, resource, *, params=None):
        return self._http_request(requests.get, resource, params=params)


    def post(self, resource, *, params=None, data=None, file_path=None):
        return self._http_request(requests.post, resource, params=params, data=data, file_upload=file_path)


    def patch(self, resource, *, params=None, data=None):
        return self._http_request(requests.patch, resource, params=params, data=data)


    def put(self, resource, *, params=None, data=None):
        """
        Makes an HTTP PUT request to Mosaic. 

        PUT differs from POST in that it assumes 
        idempotency: calling HTTP PUT twice should have 
        the same behavior as calling it once. 

        POST is used to create when the resource
        identifier is not known already. In Mosaic, 
        it usually isn't. For example,
        a POST to /samples will create a new sample, e.g.
        /samples/35 -- the resource identifier. Thus, 
        for us, PUT oftens performs updates.
        """
        return self._http_request(requests.put, resource, params=params, data=data)


    def delete(self, resource, *, params=None):
        return self._http_request(requests.delete, resource, params=params)


    def get_paged_route_iter(self, resource, *, params=None):
        """
        limit, order_by, order_dir, search come from params, if used.

        The defaults for these values are in the API docs.

        If you want a specific page, don't use this method.
        """
        limit = None
       
        if params:
            limit = params.get('limit')
            search = params.get('search')
        else:
            params = {}

        if not limit:
            limit = 50
            params['limit'] = limit

        received_count = 0

        is_exhausted = False

        page = 1

        while not is_exhausted:
            params['page'] = page
            res = self.get(resource, params=params)
            count, data = res['count'], res['data']
           
            received_count += len(data)
            page += 1

            is_exhausted = (received_count >= count or not data)

            yield from data


    """
    Project API routes.
    """

    def get_project(self, project_id):
        project_data = self.get(f'projects/{project_id}')

        project = Project(mosaic=self, project_data=project_data)

        return project


    def get_projects(self):
        for pdata in self.get_paged_route_iter('projects'):
            yield Project(mosaic=self, project_data=pdata)


    def create_project(self, name, reference='GRCh38', family_members=None, privacy_level=None, family_name=None):
        """
        family_members looks like e.g.
        [
            {
                'name': 'Proband',
                'relation': 'Proband',
                'sex': 'Female',
                'affection_status': 'Affected'
            },
            {
                'name': 'Mother',
                'relation': 'Mother',
                'sex': 'Female',
                'affection_status': 'Unaffected'
            },
        ]
        """


        # TODO: support other optional fields.
        data = { 'name': name, 'reference': reference }

        if family_members: 
            data['family_members'] = family_members

        if privacy_level: 
            data['privacy_level'] = privacy_level

        if family_name:
            data['family_name'] = family_name

        project_data = self.post('projects', data=data)

        project = Project(mosaic=self, project_data=project_data)

        return project


    def update_project(self, project_id, *, name=None, description=None):
        data = {}

        if name:
            data['name'] = name

        if description:
            data['description'] = description

        if not name and not description:
            raise Exception('Provide either name or description')

        self.put(f'projects/{project_id}', data=data)


    def delete_project(self, project_id):
        self.delete(f'projects/{project_id}')


    def request_history(self):
        """
        Return a list of all the HTTP requests run so far 
        in this session, as a list of curl commands.
        """
        return self._request_history

    """
    ATTRIBUTE FORMS
    """

    def get_attribute_forms(self):
        return self.get(f'attribute-forms')


    def post_attribute_form(self, *, name=None, attributes=None):
        data = { }
        if name: data['name'] = name
        if attributes: data['attribute_form_attributes'] = attributes

        return self.post(f'attribute-forms', data=data)


    def put_attribute_form(self, attribute_form_id, *, name=None, attributes=None):
        data = { }
        if name: data['name'] = name
        if attributes: data['attribute_form_attributes'] = attributes

        return self.put(f'attribute-forms/{attribute_form_id}', data=data)


    def delete_attribute_form(self, attribute_form_id):
        return self.delete(f'attribute-forms/{attribute_form_id}')


    """
    GENES
    """


    def get_genes(self, gene=None):
        params = { }
        if gene: params['search'] = gene

        yield from self.get_paged_route_iter(f'genes', params=params)


class Project(object):
    def __init__(self, *, mosaic_host_type='local', mosaic=None, project_id=None, project_data=None):
        """
        The constructor accepts a couple different methods of initialization,
        to be more easily used on the commandline as well as in an interpreter.

        In an interpreter, you would likely create a mosaic instance first:
            mosaic = Mosaic()
        and then use it to get a project:
            project = mosaic.get_project(project_id)

        because this way, you can make requests with either of these objects.

        On a command line, you'd likely use mosaic_host_type and project_id.
        """
        # the project gets a copy of the backing mosaic instance
        if mosaic:
            self._mosaic = mosaic
        else:
            self._mosaic = Mosaic(mosaic_host_type)

        if project_data:
            self.id = project_data['id']
            self.name = project_data['name']
            self.data = project_data
        elif project_id:
            self.id = project_id
            self.data = { 'id': project_id }
        else:
            raise Exception('Either project_data or project_id must be provided to Project()')

        self._path = f"projects/{self.id}"



    def __repr__(self):
        return f'Project({self._mosaic}, {self.data})'


    def __str__(self):
        return f"{self.name} (id: {self.id})"


    """
    COLLECTIONS
    """

    def post_sub_projects(self, *, collection_projects=None, role_type_id=None, same_role=None):
        data = { }

        if collection_projects: data['collection_projects'] = collection_projects
        if role_type_id: data['role_type_id'] = role_type_id
        if same_role: data['same_role'] = same_role

        return self._mosaic.post(f'{self._path}/sub-projects', data=data)



    """
    EXPERIMENTS
    """

    def delete_experiment(self, experiment_id):
        return self._mosaic.delete(f'{self._path}/experiments/{experiment_id}')


    def get_experiment(self, experiment_id):
        return self._mosaic.get(f'{self._path}/experiments/{experiment_id}')


    def get_experiments(self):
        return self._mosaic.get(f'{self._path}/experiments')


    def post_experiment(self, *, name=None, description=None, experiment_type=None, file_ids=None):
        data = { }

        if name: data['name'] = name
        if description: data['description'] = description
        if experiment_type: data['type'] = experiment_type
        if not file_ids: data['file_ids'] = []

        return self._mosaic.post(f'{self._path}/experiments', data=data)


    def put_experiment(self, *, name=None, description=None, experiment_type=None, file_ids=None):
        data = { }

        if name: data['name'] = name
        if description: data['description'] = description
        if experiment_type: data['type'] = experiment_type
        if not file_ids: data['file_ids'] = []

        return self._mosaic.put(f'{self._path}/experiments', data=data)



    """
    GENES
    """

    def delete_gene_set(self, gene_set_id):
        return self._mosaic.delete(f'{self._path}/genes/sets/{gene_set_id}')

    def get_gene_sets(self):
        return self._mosaic.get(f'{self._path}/genes/sets')

    def post_gene_set(self, *, name=None, description=None, is_public_to_project=None, gene_ids=None, gene_names=None):
        data = { }

        if name: data['name'] = name
        if description: data['description'] = description
        if is_public_to_project: data['is_public_to_project'] = is_public_to_project
        if gene_ids: data['gene_ids'] = gene_ids
        if gene_names: data['gene_names'] = gene_names

        return self._mosaic.post(f'{self._path}/genes/sets', data=data)



    """
    JOBS
    """

    def get_job_status(self, job_id):
        return self._mosaic.get(f'{self._path}/jobs/{job_id}')


    """
    PEDIGREE
    """

    def get_pedigree(self, sample_id):
        return self._mosaic.get(f'{self._path}/samples/{sample_id}/pedigree')


    """
    PROJECT ATTRIBUTES
    """

    def get_project_attributes(self):
        return self._mosaic.get(f'{self._path}/attributes')


    def put_project_attributes(self, attribute_id, *, description=None, name=None, predefined_values=None, value=None, is_editable=None):
        data = { }

        if description: data['description'] = description
        if is_editable: data['is_editable'] = is_editable
        if name: data['name'] = name
        if predefined_values: data['predefined_values'] = predefined_values
        if value: data['value'] = value

        return self._mosaic.put(f'{self._path}/attributes/{attribute_id}', data=data)


    """
    PROJECT DASHBOARD
    """

    def get_project_dashboard(self):
        return self._mosaic.get(f'{self._path}/dashboard')


    def post_project_dashboard(self, *, dashboard_type=None, is_active=None, should_show_name_in_badge=None, chart_id=None, attribute_id=None, project_analysis_id=None, project_conversation_id=None, variant_set_id=None):
        data = { }

        if dashboard_type: data['type'] = dashboard_type 
        if is_active: data['is_active'] = is_active 
        if should_show_name_in_badge: data['should_show_name_in_badge'] = should_show_name_in_badge 
        if chart_id: data['chart_id'] = chart_id 
        if attribute_id: data['attribute_id'] = attribute_id 
        if project_analysis_id: data['project_analysis_id'] = project_analysis_id 
        if project_conversation_id: data['project_conversation_id'] = project_conversation_id 
        if variant_set_id: data['variant_set_id'] = variant_set_id 

        return self._mosaic.post(f'{self._path}/dashboard', data=data)


    """
    PROJECT FILES
    """

    def get_project_files(self):
        yield from self._mosaic.get_paged_route_iter(f'{self._path}/files')


    def get_project_file_url(self, file_id):
        return self._mosaic.get(f'{self._path}/files/{file_id}/url')


    def delete_project_file(self, file_id):
        return self._mosaic.delete(f'{self._path}/files/{file_id}')


    def post_project_file(self, *, size=None, uri=None, endpoint_url=None, library_type=None, name=None, nickname=None, reference=None, file_type=None):
        data = { }

        if size: data['size'] = size
        if uri: data['uri'] = uri
        if endpoint_url: data['endpoint_url'] = endpoint_url
        if library_type: data['library_type'] = library_type
        if name: data['name'] = name
        if nickname: data['nickname'] = nickname
        if reference: data['reference'] = reference
        if file_type: data['file_type'] = file_type

        return self._mosaic.post(f'{self._path}/files', data=data)


    def put_project_file(self, file_id, *, size=None, uri=None, endpoint_url=None, library_type=None, name=None, nickname=None, reference=None, file_type=None):
        data = { }

        if size: data['size'] = size
        if uri: data['uri'] = uri
        if endpoint_url: data['endpoint_url'] = endpoint_url
        if library_type: data['library_type'] = library_type
        if name: data['name'] = name
        if nickname: data['nickname'] = nickname
        if reference: data['reference'] = reference
        if file_type: data['file_type'] = file_type

        return self._mosaic.put(f'{self._path}/files/{file_id}', data=data)


    """
    PROJECT SETTINGS
    """

    def get_project_settings(self):
        return self._mosaic.get(f'{self._path}/settings')


    def put_project_settings(self, *, privacy_level=None, reference=None, selected_sample_attribute_chart_data=None, selected_sample_attribute_column_ids=None, selected_variant_annotation_ids=None, default_variant_set_annotation_ids=None, sorted_annotations=None, is_template=None):
        data = { }

        if default_variant_set_annotation_ids: data['default_variant_set_annotation_ids'] = default_variant_set_annotation_ids
        if privacy_level: data['privacy_level'] = privacy_level
        if reference: data['reference'] = reference
        if selected_sample_attribute_chart_data: data['selected_sample_attribute_chart_data'] = selected_sample_attribute_chart_data
        if selected_sample_attribute_column_ids: data['selected_sample_attribute_column_ids'] = selected_sample_attribute_column_ids
        if selected_variant_annotation_ids:data['selected_variant_annotation_ids'] = selected_variant_annotation_ids
        if sorted_annotations:data['sorted_annotations'] = sorted_annotations
        if is_template: data['is_template'] = is_template

        return self._mosaic.put(f'{self._path}/settings', data=data)


    """
    PROJECTS
    """

    def get_collection_projects(self):
        return self._mosaic.get(f'{self._path}/sub-projects')


    def get_project(self):
        return self._mosaic.get(f'{self._path}/')


    def patch_project(self, template_project_id):
        return self._mosaic.patch(f'{self._path}/template/{template_project_id}')


    """
    SAMPLE ATTRIBUTES
    """

    def get_sample_attributes(self):
        return self._mosaic.get(f'{self._path}/samples/attributes')


    def get_attributes_for_sample(self, sample_id):
        return self._mosaic.get(f'{self._path}/samples/{sample_id}/attributes')


    def post_sample_attribute_value(self, sample_id, attribute_id, value):
        data = { }

        if value: data['value'] = value

        return self._mosaic.post(f'{self._path}/samples/{sample_id}/attributes/{attribute_id}', data=data)


    def put_sample_attribute_value(self, sample_id, attribute_id, value):
        data = { }

        if value: data['value'] = value

        return self._mosaic.put(f'{self._path}/samples/{sample_id}/attributes/{attribute_id}', data=data)


    def delete_sample_attribute(self, data):
        pass


    def update_sample_attribute(self, data):
        pass


    """
    SAMPLE HPO TERMS
    """

    def get_sample_hpo_terms(self, sample_id):
        return self._mosaic.get(f'{self._path}/samples/{sample_id}/hpo-terms')


    def get_samples_hpo_terms(self):
        return self._mosaic.get(f'{self._path}/samples/hpo-terms')


    def post_sample_hpo_term(self, sample_id, hpo_id):
        data = { }

        if hpo_id: data['hpo_id'] = hpo_id

        return self._mosaic.post(f'{self._path}/samples/{sample_id}/hpo-terms', data=data)


    """
    SAMPLES
    """

    def get_samples(self):
        return self._mosaic.get(f'{self._path}/samples')


    def get_sample(self, sample_id, only_keys=None):
        sample_data = self._mosaic.get(f'{self._path}/samples/{sample_id}')
    
        if only_keys:
            return { key: sample_data[key] for key in only_keys }

        return sample_data


    def update_sample(self, sample_id, *, name=None, description=None):
        """
        The API for this is a little strange.
        """
        data = {}

        if name:
            data['name'] = name

        if description:
            data['description'] = description

        if not name and not description:
            raise Exception('Provide either name or description')

        self._mosaic.put(f'{self._path}/samples/{sample_id}', data=data)


    def create_sample(self, name, description=None):
        data = { 'name': name }

        if description:
            data['description'] = description

        return self._mosaic.post(f'{self._path}/samples', data=data)


    def delete_sample(self, sample_id):
        return self._mosaic.delete(f'{self._path}/samples/{sample_id}')


    def merge_samples(self, from_sample_id, into_sample_id):
        data = {
            'from_sample_id': from_sample_id,
            'into_sample_id': into_sample_id,
        }

        return self._mosaic.post(f'{self._path}/samples/merge', data=data)

    """
    SAMPLE FILES
    """

    def get_sample_files(self, sample_id):
        yield from self._mosaic.get_paged_route_iter(f'{self._path}/samples/{sample_id}/files')


    def post_sample_file(self, sample_id, *, url=None, experiment_id=None, library_type=None, name, nickname=None, qc=None, reference, file_type, size=None, uri, vcf_sample_name=None):
        data = {
            'name': name,
            'reference': reference,
            'type': file_type,
            'uri': uri
        }

        if url: data['endpoint_url'] = url
        if experiment_id: data['experiment_id'] = experiment_id
        if library_type: data['library_type'] = library_type
        if nickname: data['nickname'] = nickname
        if qc: data['qc'] = qc
        if size: data['size'] = size
        if vcf_sample_name: data['vcf_sample_name'] = vcf_sample_name

        return self._mosaic.post(f'{self._path}/samples/{sample_id}/files', data=data)


    def put_sample_file(self, sample_id, file_id, *, url=None, experiment_id=None, library_type=None, name=None, nickname=None, qc=None, reference=None, file_type=None, size=None, uri=None, vcf_sample_name=None):
        data = {}

        if name: data['name'] = name
        if reference: data['reference'] = reference
        if file_type: data['type'] = file_type
        if uri: data['uri'] = uri
        if url: data['endpoint_url'] = url
        if experiment_id: data['experiment_id'] = experiment_id
        if library_type: data['library_type'] = library_type
        if nickname: data['nickname'] = nickname
        if qc: data['qc'] = qc
        if size: data['size'] = size
        if vcf_sample_name: data['vcf_sample_name'] = vcf_sample_name
        if not data:
          print('No fields to update were provided. Please include at least one field to update')
          exit(1)

        return self._mosaic.put(f'{self._path}/samples/{sample_id}/files/{file_id}', data=data)


    def delete_sample_file(self, sample_id, file_id):
        return self._mosaic.delete(f'{self._path}/samples/{sample_id}/files/{file_id}')


    """
    VARIANT ANNOTATIONS
    """

    def delete_variant_annotation(self, annotation_id):
        return self._mosaic.delete(f'{self._path}/variants/annotations/{annotation_id}')

    def get_variant_annotations(self):
        return self._mosaic.get(f'{self._path}/variants/annotations')

    def get_variant_annotations_to_import(self): 
        yield from self._mosaic.get_paged_route_iter(f'{self._path}/variants/annotations/import')

    def post_variant_annotation(self, *, name=None, value_type=None, privacy_level=None, display_type=None, severity=None, category=None, value_truncate_type=None, value_max_length=None):
        data = { }

        if name: data['name'] = name
        if value_type: data['value_type'] = value_type
        if privacy_level: data['privacy_level'] = privacy_level
        if display_type: data['display_type'] = display_type
        if severity: data['severity'] = severity
        if category: data['category'] = category
        if value_truncate_type: data['value_truncate_type'] = value_truncate_type
        if value_max_length: data['value_max_length'] = value_max_length

        return self._mosaic.post(f'{self._path}/variants/annotations', data=data)

    def post_import_variant_annotation(self, annotation_id):
        data = {'annotation_id': annotation_id}

        return self._mosaic.post(f'{self._path}/variants/annotations/import', data=data)

    def put_variant_annotation(self, annotation_id, *, name, value_type=None, privacy_level=None, display_type=None, severity=None, category=None, value_truncate_type=None, value_max_length=None):
        data = { 'name': name }

        if value_type: data['value_type'] = value_type
        if privacy_level: data['privacy_level'] = privacy_level
        if display_type: data['display_type'] = display_type
        if severity: data['severity'] = severity
        if category: data['category'] = category
        if value_truncate_type: data['value_truncate_type'] = value_truncate_type
        if value_max_length: data['value_max_length'] = value_max_length

        return self._mosaic.put(f'{self._path}/variants/annotations/{annotation_id}', data=data)

    """
    VARIANT FILTERS
    """

    def get_variant_filters(self):
        return self._mosaic.get(f'{self._path}/variants/filters')


    def post_variant_filter(self, *, name=None, description=None, category=None, column_uids=None, sort_column_uid=None, sort_direction=None, filter_data=None):
        data = { 'name': name, 'filter': filter_data }

        if name: data['name'] = name
        if description: data['description'] = description
        if category: data['category'] = category
        if column_uids: data['selected_variant_column_uids'] = column_uids
        if sort_column_uid: data['sort_by_column_uid'] = sort_column_uid
        if sort_direction: data['sort_dir'] = sort_direction
        if filter_data: data['filter'] = filter_data

        return self._mosaic.post(f'{self._path}/variants/filters', data=data)

    
    def update_variant_filter(self, filter_id, new_data):
        self._mosaic.put(f'{self._path}/variants/filters/{filter_id}', data=new_data)


    def delete_variant_filter(self, filter_id):
        self._mosaic.delete(f'{self._path}/variants/filters/{filter_id}')


    """
    VARIANTS
    """

    def get_variant_set(self, variant_set_id):
        return self._mosaic.get(f'{self._path}/variants/sets/{variant_set_id}')


    def get_variant_sets(self):
        return self._mosaic.get(f'{self._path}/variants/sets')


    def post_variant_file(self, file_path, upload_type=None, disable_successful_notification=None):
        data = { }

        if upload_type:
            data['type'] = upload_type
        if disable_successful_notification:
            if disable_successful_notification == 'true':
              data['disable_successful_notification'] = True
            else:
              data['disable_successful_notification'] = False

        return self._mosaic.post(f'{self._path}/variants/upload', file_path=file_path, data=data)


if __name__ == '__main__':
    import fire
    fire.Fire({
        'mosaic': Mosaic,
        'project': Project
        })


