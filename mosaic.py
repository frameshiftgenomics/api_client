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
from pprint import pprint

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

#        if not show_traceback:
#            sys.tracebacklimit = 0

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
    def _http_request(self, method, resource, *, params=None, data=None, file_upload=None, sample_map=None):

        formatted_params = {}
        """
        By forcing square brackets onto list query params, there is no ambiguity on the type.
        """
        if params:
            for key, value in params.items():
                if isinstance(value, list):
                    new_key = f"{key}[]"
                    formatted_params[new_key] = value
                else:
                    formatted_params[key] = value

        kwargs = {
                'headers': self._headers, 
                'verify': self._verify, 
                'params': formatted_params
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

            # A sample_map is a tsv file with sample ids that should only
            # be supplied if a file was also supplied
            if sample_map:
              kwargs['files']['sample_map'] = open(sample_map, "rb")
          
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


    def post(self, resource, *, params=None, data=None, file_path=None, sample_map=None):
        return self._http_request(requests.post, resource, params=params, data=data, file_upload=file_path, sample_map=sample_map)


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


    def delete(self, resource, *, params=None, data=None):
        return self._http_request(requests.delete, resource, params=params, data=data)


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
    GLOBAL ATTRIBUTE FORMS
    """

    def delete_attribute_form(self, attribute_form_id):
        return self.delete(f'attribute-forms/{attribute_form_id}')


    def get_attribute_forms(self):
        return self.get(f'attribute-forms')


    def post_attribute_form(self, *, name=None, attributes=None, origin_type=None):
        data = { }
        if name:
            data['name'] = str(name)
        if attributes:
            data['attribute_form_attributes'] = attributes
        if origin_type:
            data['origin_type'] = origin_type

        return self.post(f'attribute-forms', data=data)


    def put_attribute_form(self, attribute_form_id, *, name=None, attributes=None):
        data = { }
        if name:
            data['name'] = name
        if attributes:
            data['attribute_form_attributes'] = attributes

        return self.put(f'attribute-forms/{attribute_form_id}', data=data)


    """
    GLOBAL CONVERSATION GROUPS
    """


    def delete_conversation_group(self, group_id):
        return self.delete(f'conversation-groups/{group_id}')


    def get_conversation_group(self, group_id, include_user_info=False):
        params = { }
        if include_user_info:
            params['include_user_info'] = 'true'

        return self.get(f'conversation-groups/{group_id}', params=params)


    def get_conversation_groups(self, include_user_info=False):
        params = { }
        if include_user_info:
            params['include_user_info'] = 'true'

        return self.get(f'conversation-groups', params=params)


    def post_conversation_groups(self, name, user_ids, *, description=None):
        data = { 'name': name,
                 'user_ids': user_ids }

        if description:
            data['description'] = description

        return self.post(f'conversation-groups', data=data)


    def put_conversation_groups(self, group_id, *, name=None, description=None, user_ids=None):
        data = { }

        if description:
            data['description'] = description
        if name:
            data['name'] = name
        if user_ids:
            data['user_ids'] = user_ids

        return self.put(f'conversation-groups/{group_id}', data=data)




    """
    GLOBAL GENES
    """


    def get_genes(self, gene=None, reference=None, region=None):
        params = { }
        if gene:
            params['search'] = gene
        if region:
            params['include_region'] = 'true'
        if reference:
            params['reference'] = reference
        else:
            params['reference'] = 'GRCh38'

        yield from self.get_paged_route_iter(f'genes', params=params)


    """
    GLOBAL HPO TERMS
    """

    def get_hpo_term(self, hpo_id):
        return self.get(f'hpo-terms/{hpo_id}')


    def get_hpo_terms(self, hpo_ids):
        params = { }
        if hpo_ids:
            params['hpo_ids'] = hpo_ids

        yield from self.get_paged_route_iter(f'hpo-terms', params=params)


    """
    GLOBAL JOBS
    """

    def delete_job(self, job_id):
        return self.delete(f'jobs/{job_id}')


    def get_job_status(self, job_id):
        return self.get(f'jobs/{job_id}')


    def get_queue_status(self, *, job_statuses=None, per_status_start=None, per_status_end=None):
        params = { }
        if job_statuses:
          params['job_statuses'] = [job_statuses]
        if per_status_start:
          params['per_status_start'] = per_status_start
        if per_status_end:
          params['per_status_end'] = per_status_end

        return self.get(f'jobs', params=params)


    """
    GLOBAL POLICIES
    """

    def delete_policies(self, policy_id):
        return self.delete(f'policies/{policy_id}')


    def get_policies(self):
        return self.get(f'policies')


    def post_policies(self, name, description):

        data = { 'name': name,
                 'description': description }

        return self.post(f'policies', data=data)


    def put_policies(self, policy_id, name, description):

        data = { 'name': name,
                 'description': description }

        return self.post(f'policies/{policy_id}', data=data)


    """
    GLOBAL PROJECTS
    """

    def get_projects(self, *, search=None, only_collections=None):
        params = { }

        if only_collections:
            params['only_collections'] = 'true'
        if search:
            params['search'] = search

        yield from self.get_paged_route_iter(f'projects', params=params)


    def post_project(self, name, reference, *, nickname=None, description=None, is_collection=None, collection_projects=None, privacy_level='private', template_project_id=None):

        data = { 'name': name,
                 'reference': reference }

        if nickname:
            data['nickname'] = nickname
        if description:
            data['description'] = description
        if is_collection:
            data['is_collection'] = 'true'
        else:
            data['is_collection'] = 'false'
        if collection_projects:
            data['collection_projects'] = collection_projects
        if privacy_level:
            data['privacy_level'] = privacy_level
        if template_project_id:
            data['template_project_id'] = template_project_id

        return self.post(f'projects', data=data)


    """
    GLOBAL PROJECT ATTRIBUTES
    """

    def get_public_project_attributes(self, *, attribute_ids=None):
        params = { }

        if attribute_ids:
            params['attribute_ids'] = attribute_ids

        yield from self.get_paged_route_iter(f'projects/attributes', params=params)



    """
    GLOBAL PROJECT INTERVAL ATTRIBUTES
    """

    def get_public_project_interval_attributes(self):
        return self._mosaic.get(f'{self._path}/attributes/intervals')



    """
    GLOBAL ROLE TYPES
    """

    def get_role_type(self, role_type_id):
        return self.get(f'roles/types/{role_type_id}')


    def get_role_types(self):
        return self.get(f'roles/types')



    """
    GLOBAL S3 Bucket
    """

    def get_s3_bucket_user(self, bucket_name):
        return self.get(f's3-buckets/{bucket_name}/credentials')


    def post_s3_bucket_user(self, bucket_name, access_key_id, secret_access_key, *, endpoint_url=None):
        data = { 'access_key_id': access_key_id,
                 'secret_access_key': secret_access_key }

        if endpoint_url:
            data['endpoint_url'] = endpoint_url

        return self.post(f's3-buckets/{bucket_name}/credentials', data=data)


    """
    GLOBAL SUPER ADMIN
    """

    def delete_user_from_whitelist(self, *, email=None, delete_account=None):
        params = { 'email': email }

        if delete_account:
          params['delete_user_account'] = 'true'

        return self.delete(f'whitelist/users', params=params)


    def delete_user_project_roles(self, user_id, *, project_ids=None, remove_from_all=None):
        params = { 'remove_from_all': 'false' }

        if project_ids:
          params['project_ids'] = project_ids
        if remove_from_all:
          params['remove_from_all'] = 'true'

        return self.delete(f'users/{user_id}/roles', params=params)


    def get_user_whitelist(self):
        return self.get(f'whitelist/users')


    def get_global_settings(self):
        return self.get(f'settings')


    def get_user_by_email(self, email):
        return self.get(f'user/email/{email}')


    def get_user_info(self, user_id):
        return self.get(f'users/{user_id}')


    def get_user_project_roles(self, user_id):
        return self.get(f'users/{user_id}/roles')


    def post_to_whitelist(self, email):
        data = { 'email': email }

        return self.post(f'whitelist/users', data=data)


    """
    GLOBAL TASKS
    """


    def delete_task(self, task_id):
        return self.delete(f'tasks/{task_id}')


    def get_tasks(self, *, categories=None, completed=None, project_ids=None, types=None, order_dir=None):
        params = { }
        if categories:
            params['categories'] = categories
        if completed:
            params['completed'] = completed
        if project_ids:
            params['project_ids'] = [project_ids]
        if types:
            params['types'] = [types]
        if order_dir:
            params['order_dir'] = order_dir

        yield from self.get_paged_route_iter(f'tasks', params=params)


    """
    GLOBAL USERS
    """

    def delete_user(self, user_id):
        return self.delete(f'users/{user_id}')


    def get_user(self):
        return self.get(f'user')






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
    CLINVAR
    """

    def post_add_clinvar_version(self, *, version=None):
        data = { }

        if not version:
            print('ERROR: POST clinvar add version requires a version')
            exit(1)
        else:
            data['version'] = version

        return self._mosaic.post(f'{self._path}/variants/annotations/clinvar/versions', data=data)


    def post_diff_clinvar_version(self, *, version_a=None, version_b=None, project_ids=None, annotation_filters=None, generate_tasks=None, emails=None):
        data = { }

        if not version_a or not version_b:
            print('ERROR: POST clinvar diff version requires two ClinVar versions')
            exit(1)
        data['version_A'] = version_a
        data['version_B'] = version_b

        if project_ids:
            data['project_ids_to_check'] = project_ids

        if annotation_filters:
            data['annotation_filters'] = annotation_filters

        if generate_tasks:
            data['generate_tasks'] = generate_tasks

        if emails:
            data['emails'] = emails

        return self._mosaic.post(f'{self._path}/variants/annotations/clinvar/versions/diff', data=data)


    """
    COLLECTIONS
    """

    def delete_sub_projects(self, collection_projects):
        data = {'collection_projects': collection_projects}

        return self._mosaic.delete(f'{self._path}/sub-projects', data=data)


    def post_collection_role(self, user_id, role_type_id, *, can_download=None, can_launch_app=None, cascade_add=None):
        data = {'user_id': user_id, 'role_type_id': role_type_id}
        params = {}

        if can_download:
            data['can_download'] = can_download
        if can_launch_app:
            data['can_launch_app'] = can_launch_app
        if cascade_add:
            params['cascade_add'] = cascade_add

        return self._mosaic.post(f'{self._path}/roles', data=data, params=params)


    def post_sub_projects(self, *, collection_projects=None, role_type_id=None, same_role=None):
        data = { }

        if collection_projects:
            data['collection_projects'] = collection_projects
        if role_type_id:
            data['role_type_id'] = role_type_id
        if same_role:
            data['same_role'] = same_role

        return self._mosaic.post(f'{self._path}/sub-projects', data=data)


    def put_collection_project_settings(self, *, privacy_level=None, reference=None, selected_sample_attribute_chart_data=None, selected_sample_attribute_column_ids=None, selected_variant_annotation_version_ids=None, selected_collections_table_columns=None, selected_collection_attributes=None):
        data = { }

        if privacy_level:
            data['privacy_level'] = privacy_level
        if reference:
            data['reference'] = reference
        if selected_sample_attribute_chart_data:
            data['selected_sample_attribute_chart_data'] = selected_sample_attribute_chart_data
        if selected_sample_attribute_column_ids:
            data['selected_sample_attribute_column_ids'] = selected_sample_attribute_column_ids
        if selected_variant_annotation_version_ids:
            data['selected_variant_annotation_version_ids'] = selected_variant_annotation_version_ids
        if selected_collections_table_columns:
            data['selected_collections_table_columns'] = selected_collections_table_columns
        if selected_collection_attributes:
            data['selected_collection_attributes'] = selected_collection_attributes

        return self._mosaic.put(f'{self._path}/settings', data=data)

    """
    CONVERSATIONS
    """

    def delete_watchers(self, conversation_id, user_ids):
        data = { 'user_ids': user_ids}

        return self._mosaic.delete(f'{self._path}/conversations/{conversation_id}/watchers')


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

        if name:
          data['name'] = name
        if description:
          data['description'] = description
        if experiment_type:
          data['type'] = experiment_type
        if file_ids:
          data['file_ids'] = file_ids
        else:
          data['file_ids'] = []

        return self._mosaic.post(f'{self._path}/experiments', data=data)


    def put_experiment(self, experiment_id, *, name=None, description=None, experiment_type=None, file_ids=None):
        data = { }

        if name:
            data['name'] = name
        if description:
            data['description'] = description
        if experiment_type:
            data['type'] = experiment_type
        if file_ids:
            data['file_ids'] = file_ids
        else:
            data['file_ids'] = []

        return self._mosaic.put(f'{self._path}/experiments/{experiment_id}', data=data)



    """
    GENES
    """

    def delete_gene_set(self, gene_set_id):
        return self._mosaic.delete(f'{self._path}/genes/sets/{gene_set_id}')


    def get_gene_set(self, gene_set_id):
        return self._mosaic.get(f'{self._path}/genes/sets/{gene_set_id}')


    def get_gene_sets(self):
        return self._mosaic.get(f'{self._path}/genes/sets')


    def get_genes(self):
        yield from self.get_paged_route_iter(f'{self._path}/genes')


    def post_gene_sets(self, name, *, description=None, is_public_to_project=None, gene_ids=None, gene_names=None):
        data = { 'name': name }

        if description:
            data['description'] = description
        if is_public_to_project:
            data['is_public_to_project'] = is_public_to_project
        if gene_ids:
            data['gene_ids'] = gene_ids
        if gene_names:
            data['gene_names'] = gene_names

        return self._mosaic.post(f'{self._path}/genes/sets', data=data)


    def put_gene_sets(self, *, name=None, description=None, is_public_to_project=None, gene_ids=None, gene_names=None):
        data = { 'name': name }

        if name:
            data['name'] = name
        if description:
            data['description'] = description
        if is_public_to_project:
            data['is_public_to_project'] = is_public_to_project
        if gene_ids:
            data['gene_ids'] = gene_ids
        if gene_names:
            data['gene_names'] = gene_names

        return self._mosaic.put(f'{self._path}/genes/sets', data=data)

    """
    PEDIGREE
    """

    def get_pedigree(self, sample_id):
        return self._mosaic.get(f'{self._path}/samples/{sample_id}/pedigree')


    def post_upload_pedigree(self, *, file_path=None, create_new_samples=True):
        data = {'create_new_samples': create_new_samples}

        return self._mosaic.post(f'{self._path}/pedigree', file_path=file_path, data=data)


    """
    POLICIES
    """

    def delete_policy_resource(self, policy_id, resource_type):
        params = { 'resource_type': resource_type }

        return self._mosaic.delete(f'{self._path}/policy-resources/{policy_id}', params=params)


    def get_policy_project_resources(self, resource_type):
        params = { }

        if resource_type:
          params['type'] = resource_type

        return self._mosaic.get(f'{self._path}/policy-resources', params=params)


    def get_policy_summary(self):
        return self._mosaic.get(f'{self._path}/policies/summary')


    def post_policy_project_resource(self, policy_id, *, attribute_id=None, conversation_id=None):

        data = { 'policy_id': policy_id }

        if attribute_id:
          data['attribute_id'] = attribute_id

        if conversation_id:
          data['conversation_id'] = conversation_id

        return self._mosaic.post(f'{self._path}/policy-resources', data=data)


    def put_policy_attribute(self, policy_id, attribute_id):

        data = { 'policy_id': policy_id,
                 'attribute_id': attribute_id }

        return self._mosaic.put(f'{self._path}/policy-attributes', data=data)

    """
    PROJECT ATTRIBUTES
    """

    def delete_project_attribute(self, attribute_id):
        return self._mosaic.delete(f'{self._path}/attributes/{attribute_id}')


    def get_project_attributes(self):
        return self._mosaic.get(f'{self._path}/attributes')


    def post_import_project_attribute(self, attribute_id, *, value=None):
        data = { 'attribute_id': attribute_id}

        if value:
            data['value'] = value

        return self._mosaic.post(f'{self._path}/attributes/import', data=data)


    def post_project_attribute(self, *, description=None, name=None, predefined_values=None, value=None, value_type=None, is_editable=None, is_public=False):
        data = { }

        if description:
            data['description'] = description
        if is_editable:
            data['is_editable'] = is_editable
        if is_public:
            data['is_public'] = is_public
        if name:
            data['name'] = name
        if predefined_values:
            data['predefined_values'] = predefined_values
        if value:
            data['value'] = value
        if value_type:
            if value_type != 'float' and value_type != 'string' and value_type != 'timestamp':
              print('ERROR: Attempt to create a project attribute with value_type = ' + value_type)
              exit(1)
            data['value_type'] = value_type

        return self._mosaic.post(f'{self._path}/attributes/', data=data)


    def put_project_attributes(self, attribute_id, *, description=None, name=None, original_project_id=None, predefined_values=None, value=None, is_editable=None, display_type=None, severity=None):
        data = { }

        if description:
            data['description'] = description
        if display_type:
            data['display_type'] = display_type
        if is_editable:
            data['is_editable'] = is_editable
        if name:
            data['name'] = name
        if predefined_values:
            data['predefined_values'] = predefined_values
        if original_project_id:
            data['original_project_id'] = original_project_id
        if severity:
            data['severity'] = severity
        if value:
            data['value'] = value

        return self._mosaic.put(f'{self._path}/attributes/{attribute_id}', data=data)


    def put_update_attribute_value(self, attribute_id, value_id, *, value=None, record_date=None):
        data = { }

        if value:
            data['value'] = value
        if record_date:
            data['record_date'] = record_date

        return self._mosaic.put(f'{self._path}/attributes/{attribute_id}/values/{value_id}', data=data)


    """
    PROJECT CONVERSATIONS
    """


    def get_project_conversation(self, conversation_id):
        return self._mosaic.get(f'{self._path}/conversations/{conversation_id}')


    def get_project_conversations(self):
        return self._mosaic.get(f'{self._path}/conversations')


    """
    PROJECT DASHBOARD
    """

    def get_project_dashboard(self):
        return self._mosaic.get(f'{self._path}/dashboard')


    def post_project_dashboard(self, *, dashboard_type=None, is_active=None, should_show_name_in_badge=None, chart_id=None, attribute_id=None, project_analysis_id=None, project_conversation_id=None, variant_set_id=None):
        data = { }

        if dashboard_type:
            data['type'] = dashboard_type 
        if is_active:
            data['is_active'] = is_active 
        if should_show_name_in_badge:
            data['should_show_name_in_badge'] = should_show_name_in_badge 
        if chart_id:
            data['chart_id'] = chart_id 
        if attribute_id:
            data['attribute_id'] = attribute_id 
        if project_analysis_id:
            data['project_analysis_id'] = project_analysis_id 
        if project_conversation_id:
            data['project_conversation_id'] = project_conversation_id 
        if variant_set_id:
            data['variant_set_id'] = variant_set_id 

        return self._mosaic.post(f'{self._path}/dashboard', data=data)


    """
    PROJECT DATA GROUP ATTRIBUTES
    """


    def delete_attribute_data_group_instance(self, attribute_id, data_group_instance_id):
        return self._mosaic.delete(f'{self._path}/attributes/data-groups/{attribute_id}/instances/{data_group_instance_id}')


    def delete_project_data_group_attribute(self, attribute_id):
        return self._mosaic.delete(f'{self._path}/attributes/data-groups/{attribute_id}')


    def get_data_group_instances(self, attribute_id):
        yield from self._mosaic.get_paged_route_iter(f'{self._path}/attributes/data-groups/{attribute_id}/instances')


    def get_project_data_group_attributes(self, *, filter_restricted_project_id=None):
        params = { }
        if filter_restricted_project_id:
            params['filter_restricted_project_id'] = filter_restricted_project_id

        return self._mosaic.get(f'{self._path}/attributes/data-groups', params=params)


    def post_attribute_data_groups(self, name, *, description=None, is_public=None, is_editable=None, data_group_attributes=None):
        data = { 'name': name }
        if description:
            data['description'] = description

        if is_public:
            data['is_public'] = is_public

        if is_editable:
            data['is_editable'] = is_editable

        if data_group_attributes:
            data['data_group_attributes'] = data_group_attributes

        return self._mosaic.post(f'{self._path}/attributes/data-groups', data=data)


    def post_data_group_instance(self, attribute_id, *, record_date=None, data_group_attributes=None):
        data = { 'record_date': record_date,
                 'data_group_attribute_values': data_group_attributes}

        return self._mosaic.post(f'{self._path}/attributes/data-groups/{attribute_id}/instances', data=data)


    def post_import_project_data_group_attribute(self, attribute_id):
        data = { 'attribute_id': attribute_id }

        return self._mosaic.post(f'{self._path}/attributes/data-groups/import', data=data)


    def put_project_data_group_instance(self, attribute_id, instance_id):
        data = { }

        return self._mosaic.put(f'{self._path}/attributes/data-groups/{attribute_id}/instances/{instance_id}')#, data=data)


    def put_project_data_group_attribute(self, attribute_id, *, name=None, description=None, is_public=None, is_editable=None, data_group_attributes=None):
        data = { }

        if name:
            data['name'] = name

        if description:
            data['description'] = description

        if is_public:
            data['is_public'] = is_public

        if is_editable:
            data['is_editable'] = is_editable

        if data_group_attributes:
            data['data_group_attributes'] = data_group_attributes

        return self._mosaic.put(f'{self._path}/attributes/data-groups/{attribute_id}', data=data)


    """
    PROJECT FILES
    """


    def delete_project_file(self, file_id):
        return self._mosaic.delete(f'{self._path}/files/{file_id}')


    def get_project_files(self):
        yield from self._mosaic.get_paged_route_iter(f'{self._path}/files')


    def get_project_file_url(self, file_id):
        return self._mosaic.get(f'{self._path}/files/{file_id}/url')


    def post_project_file(self, *, size=None, uri=None, endpoint_url=None, library_type=None, name=None, nickname=None, reference=None, file_type=None):
        data = { }

        if size:
            data['size'] = size
        if uri:
            data['uri'] = uri
        if endpoint_url:
            data['endpoint_url'] = endpoint_url
        if library_type:
            data['library_type'] = library_type
        if name:
            data['name'] = name
        if nickname:
            data['nickname'] = nickname
        if reference:
            data['reference'] = reference
        if file_type:
            data['type'] = file_type
        else:
            print('The "type" is required to POST a project file')
            exit(1)

        return self._mosaic.post(f'{self._path}/files', data=data)


    def put_project_file(self, file_id, *, size=None, uri=None, endpoint_url=None, library_type=None, name=None, nickname=None, reference=None, file_type=None):
        data = { }

        if size:
            data['size'] = size
        if uri:
            data['uri'] = uri
        if endpoint_url: 
            data['endpoint_url'] = endpoint_url
        if library_type:
            data['library_type'] = library_type
        if name:
            data['name'] = name
        if nickname:
            data['nickname'] = nickname
        if reference:
            data['reference'] = reference
        if file_type:
            data['type'] = file_type

        return self._mosaic.put(f'{self._path}/files/{file_id}', data=data)


    """
    PROJECT INTERVAL ATTRIBUTES
    """

    def delete_project_interval_attribute(self, interval_attribute_id):
        return self._mosaic.delete(f'{self._path}/attributes/intervals/{interval_attribute_id}')


    def get_project_interval_attributes(self):
        return self._mosaic.get(f'{self._path}/attributes/intervals')


    def post_import_project_interval_attribute(self, attribute_id):
        data = { 'attribute_id': attribute_id}

        return self._mosaic.post(f'{self._path}/attributes/intervals/import', data=data)


    def post_project_interval_attribute(self, name, start_attribute_id, end_attribute_id, *, description=None, is_public=None, policy_ids=None):
        data = { 'name': name,
                 'start_attribute_id': start_attribute_id,
                 'end_attribute_id': end_attribute_id}

        if description:
            data['description'] = description

        if is_public:
            data['is_public'] = is_public

        if policy_ids:
            data['policy_ids'] = policy_ids

        return self._mosaic.post(f'{self._path}/attributes/intervals', data=data)



    """
    PROJECT ROLES
    """

    def delete_role(self, role_id, *, disable_cascade=None):
        params = { 'cascade': 'true'}

        if disable_cascade:
            params['cascade'] = 'false'

        return self._mosaic.delete(f'{self._path}/roles/{role_id}', params=params)


    def get_roles(self, include_sub_project_roles=None):
        params = { }

        if include_sub_project_roles:
            params['include_sub_project_roles'] = 'true'

        return self._mosaic.get(f'{self._path}/roles', params=params)


    def post_project_role(self, user_id, role_type_id, *, can_download=None, can_launch_app=None, policy_ids=None):
        data = { 'role_type_id': role_type_id}

        if can_download:
            data['can_download'] = can_download

        if can_launch_app:
            data['can_launch_app'] = can_launch_app

        if policy_ids:
            data['policy_ids'] = policy_ids

        return self._mosaic.post(f'{self._path}/roles/{role_id}', data=data)


    def put_project_role(self, role_id, role_type_id, *, user_id=None, can_download=None, can_launch_app=None, policy_ids=None):
        data = { 'role_type_id': role_type_id}

        if user_id:
            data['user_id'] = user_id

        if can_download:
            data['can_download'] = can_download

        if can_launch_app:
            data['can_launch_app'] = can_launch_app

        if policy_ids:
            data['policy_ids'] = policy_ids

        return self._mosaic.put(f'{self._path}/roles/{role_id}', data=data)



    """
    PROJECT SETTINGS
    """

    def get_project_settings(self):
        return self._mosaic.get(f'{self._path}/settings')


    def put_project_settings(self, *, external_url=None, privacy_level=None, reference=None, selected_sample_attribute_chart_data=None, selected_sample_attribute_column_ids=None, selected_variant_annotation_version_ids=None, default_variant_set_annotation_ids=None, sorted_annotations=None, is_template=None):
        data = { }

        if external_url:
            data['external_url'] = external_url
        if default_variant_set_annotation_ids:
            data['default_variant_set_annotation_ids'] = default_variant_set_annotation_ids
        if privacy_level:
            allowed_values = ['public',
                              'protected',
                              'private']
            if privacy_level not in allowed_values:
              print('Unknown privacy level: ', privacy_level, sep = '')
              exit(1)

            data['privacy_level'] = privacy_level
        if reference:
            data['reference'] = reference
        if selected_sample_attribute_chart_data:
            data['selected_sample_attribute_chart_data'] = selected_sample_attribute_chart_data
        if selected_sample_attribute_column_ids:
            data['selected_sample_attribute_column_ids'] = selected_sample_attribute_column_ids
        if selected_variant_annotation_version_ids:
            data['selected_variant_annotation_version_ids'] = selected_variant_annotation_version_ids
        if sorted_annotations:
            data['sorted_annotations'] = sorted_annotations
        if is_template:
            data['is_template'] = is_template

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

    def delete_sample_attribute(self, attribute_id):
        return self._mosaic.delete(f'{self._path}/samples/attributes/{attribute_id}')


    def get_sample_attributes(self, *, is_custom=None, include_values=None, attribute_ids=None):
        params = { }
        if is_custom:
              params['is_custom'] = is_custom
        if include_values:
              params['include_values'] = include_values
        if attribute_ids:
              params['attribute_ids'] = attribute_ids

        return self._mosaic.get(f'{self._path}/samples/attributes', params=params)


    def get_attributes_for_sample(self, sample_id):
        return self._mosaic.get(f'{self._path}/samples/{sample_id}/attributes')


    def post_import_sample_attribute(self, attribute_id):
        data = { 'attribute_id': attribute_id}

        return self._mosaic.post(f'{self._path}/samples/attributes/import', data=data)


    def post_sample_attribute_value(self, sample_id, attribute_id, value):
        data = { }

        if value: data['value'] = value

        return self._mosaic.post(f'{self._path}/samples/{sample_id}/attributes/{attribute_id}', data=data)


    def put_sample_attribute_value(self, sample_id, attribute_id, value):
        data = { }

        if value: data['value'] = value

        return self._mosaic.put(f'{self._path}/samples/{sample_id}/attributes/{attribute_id}', data=data)


    def update_sample_attribute(self, data):
        pass


    """
    SAMPLE HPO TERMS
    """

    def delete_sample_hpo_term(self, sample_id, hpo_term_id):
        return self._mosaic.delete(f'{self._path}/samples/{sample_id}/hpo-terms/{hpo_term_id}')


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

    def delete_sample(self, sample_id):
        return self._mosaic.delete(f'{self._path}/samples/{sample_id}')


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

    def delete_sample_file(self, sample_id, file_id):
        return self._mosaic.delete(f'{self._path}/samples/{sample_id}/files/{file_id}')


    def get_all_sample_files(self, *, file_types=None, sample_names=None, combine_duplicates=None):
        params = {}
        if combine_duplicates:
            params['combine_duplicates'] = combine_duplicates
        if file_types:
            params['file_types'] = file_types
        if sample_names:
            params['sample_names'] = sample_names

        yield from self._mosaic.get_paged_route_iter(f'{self._path}/samples/files', params=params)


    def get_sample_files(self, sample_id):
        yield from self._mosaic.get_paged_route_iter(f'{self._path}/samples/{sample_id}/files')


    def get_sample_file_url(self, file_id):
        return self._mosaic.get(f'{self._path}/files/{file_id}/url')


    def post_sample_file(self, sample_id, *, url=None, experiment_id=None, library_type=None, name, nickname=None, qc=None, reference, file_type, size=None, uri, vcf_sample_name=None):
        data = {
            'name': name,
            'reference': reference,
            'type': file_type,
            'uri': uri
        }

        if url:
            data['endpoint_url'] = url
        if experiment_id:
            data['experiment_id'] = experiment_id
        if library_type:
            data['library_type'] = library_type
        if nickname:
            data['nickname'] = nickname
        if qc:
            data['qc'] = qc
        if size:
            data['size'] = size
        if vcf_sample_name:
            data['vcf_sample_name'] = vcf_sample_name

        return self._mosaic.post(f'{self._path}/samples/{sample_id}/files', data=data)


    def put_sample_file(self, sample_id, file_id, *, url=None, experiment_id=None, library_type=None, name=None, nickname=None, qc=None, reference=None, file_type=None, size=None, uri=None, vcf_sample_name=None):
        data = {}

        if name:
            data['name'] = name
        if reference:
            data['reference'] = reference
        if file_type:
            data['type'] = file_type
        if uri:
            data['uri'] = uri
        if url:
            data['endpoint_url'] = url
        if experiment_id:
            data['experiment_id'] = experiment_id
        if library_type:
            data['library_type'] = library_type
        if nickname:
            data['nickname'] = nickname
        if qc:
            data['qc'] = qc
        if size:
            data['size'] = size
        if vcf_sample_name:
            data['vcf_sample_name'] = vcf_sample_name
        if not data:
          print('No fields to update were provided. Please include at least one field to update')
          exit(1)

        return self._mosaic.put(f'{self._path}/samples/{sample_id}/files/{file_id}', data=data)



    """
    TASKS
    """

    def delete_task(self, task_id):
        return self._mosaic.delete(f'{self._path}/tasks/{task_id}')


    def get_project_tasks(self):
        return self._mosaic.get(f'{self._path}/tasks')



    """
    USER PROJECT SETTINGS
    """

    def delete_user_project_settings(self):
        return self._mosaic.delete(f'{self._path}/settings')


    def get_user_project_settings(self):
        return self._mosaic.get(f'{self._path}/settings')



    """
    VARIANT ANNOTATIONS
    """

    def delete_variant_annotation(self, annotation_id):
        return self._mosaic.delete(f'{self._path}/variants/annotations/{annotation_id}')


    def delete_variant_annotation_version(self, annotation_id, annotation_version_id):
        return self._mosaic.delete(f'{self._path}/variants/annotations/{annotation_id}/versions/{annotation_version_id}')


    def delete_variant_annotation_version_values(self, annotation_id, annotation_version_id):
        return self._mosaic.delete(f'{self._path}/variants/annotations/{annotation_id}/versions/{annotation_version_id}/values')


    def get_variant_annotations(self, *, annotation_ids=None, annotation_version_ids=None, include_values=None):
        params = { }
        if annotation_ids:
            params['annotation_ids'] = annotation_ids
        if annotation_version_ids:
            params['annotation_version_ids'] = annotation_version_ids
        if include_values:
            params['include_values'] = include_values

        return self._mosaic.get(f'{self._path}/variants/annotations', params=params)


    def get_variant_annotations_to_import(self): 
        yield from self._mosaic.get_paged_route_iter(f'{self._path}/variants/annotations/import')


    def get_variant_annotation_versions(self, annotation_id):
        return self._mosaic.get(f'{self._path}/variants/annotations/{annotation_id}/versions')

    def post_variant_annotation(self, *, name=None, allow_deletion='true', value_type=None, privacy_level=None, display_type=None, severity=None, category=None, value_truncate_type=None, value_max_length=None, version=None):
        data = { }

        if allow_deletion:
            if allow_deletion == 'true':
                data['allow_deletion'] = 'true'
            elif allow_deletion == 'True':
                data['allow_deletion'] = 'true'
            elif allow_deletion == True:
                data['allow_deletion'] = 'true'
            elif allow_deletion == 'false':
                data['allow_deletion'] = 'false'
            elif allow_deletion == 'false':
                data['allow_deletion'] = 'false'
            elif allow_deletion == True:
                data['allow_deletion'] = 'false'
            else:
                print('ERROR: Upload annotations has "allow_deletion" set to ', allow_deletion, '. The value must be "true" or "false"', sep = '')
                exit(1)
        if name:
            data['name'] = name
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
        if version:
            data['version'] = version

        return self._mosaic.post(f'{self._path}/variants/annotations', data=data)

    def post_import_annotation(self, annotation_id):
        data = {'annotation_id': annotation_id}

        return self._mosaic.post(f'{self._path}/variants/annotations/import', data=data)

    def post_annotation_file(self, file_path, allow_deletion=None, disable_successful_notification=None):
        data = { }

        if allow_deletion:
            if allow_deletion == 'true':
                data['allow_deletion'] = 'true'
            else:
                data['allow_deletion'] = 'false'

        if disable_successful_notification:
            if disable_successful_notification == 'true':
                data['disable_successful_notification'] = 'true'
            else:
                data['disable_successful_notification'] = 'false'

        return self._mosaic.post(f'{self._path}/variants/annotations/upload', file_path=file_path, data=data)


    def post_create_annotation_version(self, annotation_id, version_name):
        data = { 'version': version_name }

        return self._mosaic.post(f'{self._path}/variants/annotations/{annotation_id}/versions', data=data)


    def put_variant_annotation(self, annotation_id, *, name=None, value_type=None, privacy_level=None, display_type=None, severity=None, category=None, value_truncate_type=None, value_max_length=None, latest_version_id=None):
        data = { }

        if name:
            data['name'] = name
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
        if latest_version_id:
            data['latest_annotation_version_id'] = latest_version_id

        return self._mosaic.put(f'{self._path}/variants/annotations/{annotation_id}', data=data)

    """
    VARIANT FILTERS
    """

    def delete_variant_filter(self, filter_id):
        self._mosaic.delete(f'{self._path}/variants/filters/{filter_id}')


    def get_variant_filters(self):
        return self._mosaic.get(f'{self._path}/variants/filters')


    def post_variant_filter(self, *, name=None, description=None, category=None, column_ids=None, sort_column_id=None, sort_direction=None, filter_data=None):
        data = { 'name': name, 'filter': filter_data }

        if name:
            data['name'] = name
        if description:
            data['description'] = description
        if category:
            data['category'] = category
        if column_ids:
            data['selected_view_columns_annotation_versions'] = column_ids
        if sort_column_id:
            data['sort_by_column_id'] = sort_column_id
        if sort_direction:
            if sort_direction == 'asc':
                data['sort_dir'] = 'ASC'
            elif sort_direction == 'ASC':
                data['sort_dir'] = 'ASC'
            elif sort_direction == 'ascending':
                data['sort_dir'] = 'ASC'
            elif sort_direction == 'Ascending':
                data['sort_dir'] = 'ASC'
            elif sort_direction == 'desc':
                data['sort_dir'] = 'DESC'
            elif sort_direction == 'DESC':
                data['sort_dir'] = 'DESC'
            elif sort_direction == 'descending':
                data['sort_dir'] = 'DESC'
            elif sort_direction == 'Descending':
                data['sort_dir'] = 'DESC'
            else:
                print('Unknown sort direction: ', sort_direction, sep = '')
                exit(1)
        if filter_data:
            data['filter'] = filter_data

        return self._mosaic.post(f'{self._path}/variants/filters', data=data)

    
    def update_variant_filter(self, filter_id, new_data):
        self._mosaic.put(f'{self._path}/variants/filters/{filter_id}', data=new_data)


    """
    VARIANTS
    """

    def delete_variant_set(self, variant_set_id):
        return self._mosaic.delete(f'{self._path}/variants/sets/{variant_set_id}')


    def get_variant_by_position(self, variant_position, *, include_annotation_data=None, include_genotype_data=None):
        params = { }
        params['include_annotation_data'] = 'true' if include_annotation_data else 'false'
        params['include_genotype_data'] = 'true' if include_genotype_data else 'false'

        return self._mosaic.get(f'{self._path}/variants/position/{variant_position}')


    def get_variant_set(self, variant_set_id, *, include_variant_data=None, include_genotype_data=None):
        params = { }
        params['include_variant_data'] = 'true' if include_variant_data else 'false'
        params['include_genotype_data'] = 'true' if include_genotype_data else 'false'

        return self._mosaic.get(f'{self._path}/variants/sets/{variant_set_id}')


    def get_variant_watchlist(self, *, include_variant_data=None):
        params = { }

        params['include_variant_data'] = 'true' if include_variant_data else 'false'

        return self._mosaic.get(f'{self._path}/variants/sets/watchlist', params=params)


    def get_variant_sets(self):
        return self._mosaic.get(f'{self._path}/variants/sets')


    def get_variant(self, variant_id, *, include_annotation_data=None, include_genotype_data=None):
        params = { }
        if include_annotation_data:
          if include_annotation_data == 'true':
              params['include_annotation_data'] = 'true'
          elif include_annotation_data == 'false':
              params['include_annotation_data'] = 'false'
          else:
              print('get_variant: include_annotation_data must be "true" or "false"')
              exit(1)

        if include_genotype_data:
          if include_genotype_data == 'true':
              params['include_genotype_data'] = 'true'
          elif include_genotype_data == 'false':
              params['include_genotype_data'] = 'false'
          else:
              print('get_variant: include_genotype_data must be "true" or "false"')
              exit(1)

        return self._mosaic.get(f'{self._path}/variants/{variant_id}', params=params)


    def post_variant_file(self, file_path, *, sample_map=None, upload_type=None, disable_successful_notification=None):
        data = { }

        if upload_type:
            data['type'] = upload_type
        if disable_successful_notification:
            if disable_successful_notification == 'true':
              data['disable_successful_notification'] = 'true'
            else:
              data['disable_successful_notification'] = 'false'

        return self._mosaic.post(f'{self._path}/variants/upload', file_path=file_path, data=data, sample_map=sample_map)


    def post_variant_set_annotations(self, variant_set_id, annotation_version_ids):
        data = { }

        if annotation_version_ids:
            data['selected_variant_annotation_version_ids'] = annotation_version_ids

        return self._mosaic.post(f'{self._path}/variants/sets/{variant_set_id}/annotations', data=data)


if __name__ == '__main__':
    import fire
    fire.Fire({
        'mosaic': Mosaic,
        'project': Project
        })


