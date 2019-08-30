import os
import sys
import gettext
from time import sleep
from argparse import ArgumentParser
from functools import partial
from subprocess import check_call

_ = gettext.gettext

REPOSITORY_URL = 'https://github.com/vsevolod-skripnik/vash.git'


class Project:
    SERVICE_NAMES = ('bundler', 'engine', 'proxy')

    def __init__(self, name):
        print(_(f'Initializing project “{name}”...'))
        self.name = name

        # Folders

        # ~/projects/vash/manage.py
        self.manage_file_path = os.path.abspath(__file__)
        # ~/projects/vash
        self.repository_folder_path = os.path.sep.join(
            self.manage_file_path.split(os.path.sep)[:-1]
        )
        # ~/projects
        self.projects_folder_path = os.path.sep.join(
            self.repository_folder_path.split(os.path.sep)[:-1]
        )
        # ~/projects/{name}
        self.project_folder_path = f'{self.projects_folder_path}/{name}'
        
        # ~/projects/{name}/versions
        self.versions_folder_path = f'{self.project_folder_path}/versions'
        # ~/projects/{name}/versions/latest -> ~/projects/vash
        self.latest_version_path = f'{self.versions_folder_path}/latest'
        
        # ~/projects/{name}/resources
        self.resources_folder_path = f'{self.project_folder_path}/resources'
        # ~/projects/{name}/resources/{resource}
        self.resource_folder_paths = {
            'assets': f'{self.resources_folder_path}/assets',
            'certificates': f'{self.resources_folder_path}/certificates',
            'files': f'{self.resources_folder_path}/files',
            'pages': f'{self.resources_folder_path}/pages',
            'scripts': f'{self.resources_folder_path}/scripts',
            'styles': f'{self.resources_folder_path}/styles',
            'templates': f'{self.resources_folder_path}/templates',

        }
        # ~/projects/{name}/resources/pages/_html
        self.html_pages_folder_path = f'{self.resource_folder_paths["pages"]}/_html'
        
        self.create_folders()

        # Versions

        self.version = 'latest'
        self.version_folder_path = f'{self.versions_folder_path}/{self.version}'
        if not os.path.islink(self.latest_version_path):
            print(_(f'  “{self.latest_version_path}”'))
            print(_(f'   -> “{self.repository_folder_path}”'))
            os.symlink(self.repository_folder_path, self.latest_version_path, target_is_directory=True)
        #
        self.installed_versions = os.listdir(self.versions_folder_path)

        # Environment

        self.environment = self.get_environment()

    def create_folders(self):
        print(_('Creating folders...'))

        folder_paths = [
            self.project_folder_path,
            self.versions_folder_path,
            self.resources_folder_path,
        ]
        for folder_path in folder_paths:
            print(_(f'  “{folder_path}”'))
            if not os.path.isdir(folder_path):
                os.makedirs(folder_path)

        for resource_name, resource_folder_path in self.resource_folder_paths.items():
            print(_(f'  “{resource_folder_path}”'))
            if not os.path.isdir(resource_folder_path):
                os.makedirs(resource_folder_path)
        else:
            print()

    def install(self, version):
        print(_(f'Installing version “{version}”'))

        working_folder_before_install = os.getcwd()

        version_folder_path = f'{self.versions_folder_path}/{version}'

        os.chdir(self.versions_folder_path)
        command = ['git', 'clone', f'{REPOSITORY_URL}', f'{version}']
        check_call(command)

        os.chdir(version_folder_path)
        command = ['git', 'checkout', f'{version_folder_path}']
        check_call(command)

        command = ['git', 'reset', '--hard']
        check_call(command)

        os.chdir(working_folder_before_install)

        self.installed_versions.append(version)
        print()

    def get_environment(self):
        environment_variables = {
            'USER_ID': f'{os.getuid()}',
            'RESOURCES_FOLDER': f'{self.resources_folder_path}',
        }

        for service_name in self.SERVICE_NAMES:
            variable_name = f'DOCKER_{service_name.upper()}_IMAGE'
            variable_value = f'{self.name}_{service_name}:{self.version}'
            environment_variables[variable_name] = variable_value

        for resource_name, resource_folder_path in self.resource_folder_paths.items():
            variable_name = f'{resource_name.upper()}_FOLDER'
            environment_variables[variable_name] = f'{resource_folder_path}'

        return environment_variables

    def set_environment(self):
        print('Setting environment...')
        self.environment = self.get_environment()
        for variable_name, variable_value in self.environment.items():
            print(_(f'  “{variable_name}” = “{variable_value}”'))
            os.environ[variable_name] = variable_value
        print()

    def run(self, version, as_daemon=False):
        if version not in self.installed_versions:
            self.install(version)

        self.version = version
        self.version_folder_path = f'{self.versions_folder_path}/{version}'

        print(_(f'Running “{self.name}” version “{version}”...'))
        self.set_environment()

        command = [
            'docker-compose',
                '-f', f'{self.version_folder_path}/compose/engine.yml',
                '-f', f'{self.version_folder_path}/compose/proxy.yml',
                '-f', f'{self.version_folder_path}/compose/bundler.yml',
                '--project-directory', f'{self.version_folder_path}',
                '--project-name', f'{self.name}',
                'up',
                '--build',
        ]
        if as_daemon:
            command.append('--detach')
        check_call(command)

        print()

    def create_index_page(self):
        print(_('Creating index page...'))

        if not os.path.isdir(self.html_pages_folder_path):
            os.makedirs(self.html_pages_folder_path)

        page_path = f'{self.html_pages_folder_path}/index.html'
        if not os.path.isfile(page_path):
            page_content = (
                '<!DOCTYPE html>'
                '<html>'
                '  <head>'
                '    <meta charset="utf-8">'
                '     <title>Test</title>'
                '  </head>'
                '  <body>'
                '    <p>Test</p>'
                '  </body>'
                '</html>'
            )
            with open(page_path, 'w') as file:
                file.write(page_content)
            print(_('  Done.'))
        else:
            print(_('  Exists.'))
        print()
    
    def test_index_page(self):
        print(_('Testing index page...'))
        import requests
        url = 'https://127.0.0.1/'
        max_tries = 3
        for _ in range(max_tries):
            try:
                response = requests.get(url, verify=False)
            except requests.exceptions.ConnectionError:
                print('  Fail. Sleep 5 seconds...')
                sleep(5)
            else:
                if response.status_code == 200:
                    message = 'Fine.'
                    is_fine = True
                    break
                else:
                    message = f'Oh no: {response.status_code}'
                    is_fine = False
                    break
        else:
            message = 'Max tries exceeded.'
            is_fine = False

        print(f'  {message}')
        print()
        return is_fine


def initialize_project(name):
    Project(name)


def run_project(name, version, as_daemon):
    project = Project(name)
    project.run(version, as_daemon)


def deploy_project(name, version):
    project = Project(name)
    project.run(version, as_daemon=True)
    project.create_index_page()
    print(project.test_index_page())


def get_command(argv):
    category_parser = ArgumentParser()
    category_parser.add_argument('category')
    namespace, arguments = category_parser.parse_known_args(argv[1:])

    if namespace.category == 'initialize':
        argument_parser = ArgumentParser()
        argument_parser.add_argument('name', help=_('Project name.'))
        command_function = initialize_project

    elif namespace.category == 'run':
        argument_parser = ArgumentParser()
        argument_parser.add_argument('name', help=_('Project name.'))
        argument_parser.add_argument(
            '-v', '--version', default='latest', help=_('Project version.')
        )
        argument_parser.add_argument(
            '-d', '--daemon', dest='as_daemon', 
            action='store_true', help=_('Enter daemon mode after start.')
        )
        command_function = run_project

    else:
        raise SystemExit(_(f'Unknown command category {namespace.category}.'))

    command_arguments = argument_parser.parse_args(arguments)
    return partial(command_function, **vars(command_arguments))


if __name__ == '__main__':
    command = get_command(sys.argv)
    command()