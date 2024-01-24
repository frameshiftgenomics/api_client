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
    def _http_request(self, method, resource, *, params=None, data=None):
        kwargs = {
                'headers': self._headers, 
                'verify': self._verify, 
                'params': params
                }

        if data:
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


    def post(self, resource, *, params=None, data=None):
        return self._http_request(requests.post, resource, params=params, data=data)


    def patch(self, resource, *, params=None, data=None):
        print('terst')
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


    def create_project(self, name, reference='GRCh38', family_members=None):
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
    PROJECT ATTRIBUTES
    """

    def get_project_attributes(self):
        return self._mosaic.get(f'{self._path}/attributes')


    """
    PROJECT DASHBOARD
    """

    def get_project_dashboard(self):
        return self._mosaic.get(f'{self._path}/dashboard')



    """
    PROJECT SETTINGS
    """

    def get_project_settings(self):
        return self._mosaic.get(f'{self._path}/settings')


    def put_project_settings(self, *, privacy_level=None, reference=None, selected_sample_attribute_chart_data=None, selected_sample_attribute_column_ids=None, selected_variant_annotation_ids=None, sorted_annotations=None, is_template=None):
        data = { }

        if privacy_level:
            data['privacy_level'] = privacy_level

        if reference:
            data['reference'] = reference

        if selected_sample_attribute_chart_data:
            data['selected_sample_attribute_chart_data'] = selected_sample_attribute_chart_data

        if selected_sample_attribute_column_ids:
            data['selected_sample_attribute_column_ids'] = selected_sample_attribute_column_ids

        if selected_variant_annotation_ids:
            data['selected_variant_annotation_ids'] = selected_variant_annotation_ids

        if sorted_annotations:
            data['sorted_annotations'] = sorted_annotations

        if is_template:
            data['is_template'] = is_template

        return self._mosaic.put(f'{self._path}/settings', data=data)


    """
    PROJECTS
    """

    def patch_project(self, template_project_id):
        return self._mosaic.patch(f'{self._path}/template/{template_project_id}')


    """
    SAMPLE ATTRIBUTES
    """

    def get_sample_attributes(self):
        return self._mosaic.get(f'{self._path}/samples/attributes')


    def get_attributes_for_sample(self, sample_id):
        return self._mosaic.get(f'{self._path}/samples/{sample_id}/attributes')


    def set_sample_attribute_value(self, sample_id, attr_id, value):
        pass


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


    def post_sample_file(self, sample_id):
        data = { 'name': name }

        if description:
            data['description'] = description

        return self._mosaic.post(f'{self._path}/samples', data=data)


    def delete_sample_file(self, sample_id, file_id):
        return self._mosaic.delete(f'{self._path}/samples/{sample_id}/files/{file_id}')


    """
    VARIANT ANNOTATIONS
    """

    def get_variant_annotations(self):
        return self._mosaic.get(f'{self._path}/variants/annotations')

    def get_variant_annotations_to_import(self): 
        yield from self._mosaic.get_paged_route_iter(f'{self._path}/variants/annotations/import')

    def put_variant_annotation(self, annotation_id, *, name, value_type=None, privacy_level=None, display_type=None, severity=None, category=None, value_truncate_type=None, value_max_length=None):
        data = { 'name': name }

        if value_type:
            data['value_type'] = value_type

        if privacy_level:
            data['privacy_level'] = privacy_level

        if display_type:
            data['display_type'] = display_type

        if severity:
            data['severity'] = severity

        if category:
            data['category'] = category

        if value_truncate_type:
            data['value_truncate_type'] = value_truncate_type

        if value_max_length:
            data['value_max_length'] = value_max_length

        return self._mosaic.put(f'{self._path}/variants/annotations/{annotation_id}', data=data)

    def create_variant_annotation(self, *, name, value_type=None, privacy_level=None, display_type=None, severity=None, category=None, value_truncate_type=None, value_max_length=None):
        data = { 'name': name }

        if value_type:
            data['value_type'] = value_type

        if privacy_level:
            data['privacy_level'] = privacy_level

        if display_type:
            data['display_type'] = display_type

        if severity:
            data['severity'] = severity

        if category:
            data['category'] = category

        if value_truncate_type:
            data['value_truncate_type'] = value_truncate_type

        if value_max_length:
            data['value_max_length'] = value_max_length

        return self._mosaic.post(f'{self._path}/variants/annotations', data=data)

    """
    VARIANT FILTERS
    """

    def get_variant_filters(self):
        return self._mosaic.get(f'{self._path}/variants/filters')


    def post_variant_filter(self, *, name=None, description=None, category=None, column_uids=None, sort_column_uid=None, sort_direction=None, filter_data=None):
        data = { 'name': name, 'filter': filter_data }
        if name:
            data['name'] = name

        if description:
            data['description'] = description

        if category:
            data['category'] = category

        if column_uids:
            data['selected_variant_column_uids'] = column_uids

        if sort_column_uid:
            data['sort_by_column_uid'] = sort_column_uid

        if sort_direction:
            data['sort_dir'] = sort_direction

        if filter_data:
            data['filter'] = filter_data

        return self._mosaic.post(f'{self._path}/variants/filters', data=data)

    
    def update_variant_filter(self, filter_id, new_data):
        self._mosaic.put(f'{self._path}/variants/filters/{filter_id}', data=new_data)


    def delete_variant_filter(self, filter_id):
        self._mosaic.delete(f'{self._path}/variants/filters/{filter_id}')


if __name__ == '__main__':
    import fire
    fire.Fire({
        'mosaic': Mosaic,
        'project': Project
        })


