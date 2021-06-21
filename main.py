import datetime

import webapp2
import jinja2
import os
from google.appengine.api import users
from google.appengine.ext import ndb

from gpu import GPU

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True
)


class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        user = users.get_current_user()
        if user:
            url = users.create_logout_url(self.request.uri)
            url_string = 'logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_string = 'login'
        template_values = {
            'url': url,
            'url_string': url_string,
            'user': user,
            'gpu_list': GPU.query()
        }

        action = self.request.get('action')
        if not action:
            template = JINJA_ENVIRONMENT.get_template('main.html')
            self.response.write(template.render(template_values))

        elif action == 'filter-gpu':
            template_values['gpu_list'], query = self.filter_gpu(self.request)
            template_values.update(query)
            template = JINJA_ENVIRONMENT.get_template('main.html')
            self.response.write(template.render(template_values))

    def post(self):
        action = self.request.get('action')
        if action == "add-gpu":
            message, redirect = self.add_gpu(self.request)

        template_values = {
            'message': message,
            'redirect': redirect,
        }
        template = JINJA_ENVIRONMENT.get_template('message.html')
        self.response.write(template.render(template_values))

    def add_gpu(self, req):
        name = req.get('name')
        key = ndb.Key('GPU', name)
        gpu = key.get()

        if gpu is None:
            gpu = GPU(id=name)
            gpu.name = name
            gpu.manufacturer = req.get('mfg')
            gpu.dateIssued = datetime.datetime.strptime(req.get('date'), '%Y-%m-%d')

            gpu.geometryShader = self.request.get('geo-sh').lower() == 'on'
            gpu.tesselationShader = self.request.get('tsl-sh').lower() == 'on'
            gpu.shaderInt16 = self.request.get('sh-16').lower() == 'on'
            gpu.sparseBinding = self.request.get('sp-bind').lower() == 'on'
            gpu.textureCompressionETC2 = self.request.get('tc-etc2').lower() == 'on'
            gpu.has_vertex_pipeline_stores_and_atomics = self.request.get('vpsa').lower() == 'on'

            gpu.put()

            return 'New GPU entry successfully registered in system', '/'

        else:
            return 'ERROR! A GPU with similar name is already present in the system', '/'

    def filter_gpu(self, req):
        gpus = GPU.query()
        query = {
            'geo_sh': self.request.get('geo-sh').lower() == 'on',
            'tsl_sh': self.request.get('tsl-sh').lower() == 'on',
            'sh_16': self.request.get('sh-16').lower() == 'on',
            'sp_bind': self.request.get('sp-bind').lower() == 'on',
            'tc_etc2': self.request.get('tc-etc2').lower() == 'on',
            'vpsa': self.request.get('vpsa').lower() == 'on',
        }
        if query['geo_sh']:
            gpus = gpus.filter(GPU.geometryShader == True)
        if query['tsl_sh']:
            gpus = gpus.filter(GPU.tesselationShader == True)
        if query['sh_16']:
            gpus = gpus.filter(GPU.shaderInt16 == True)
        if query['sp_bind']:
            gpus = gpus.filter(GPU.sparseBinding == True)
        if query['tc_etc2']:
            gpus = gpus.filter(GPU.textureCompressionETCS2 == True)
        if query['vpsa']:
            gpus = gpus.filter(GPU.vertexPipelineStoresAndAtomics == True)
        gpus = gpus.fetch()

        return gpus, query


class ShowPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        user = users.get_current_user()
        name = self.request.get('name')
        key = ndb.Key('GPU', name)
        template_values = {'user': user, 'gpu': key.get()}
        template = JINJA_ENVIRONMENT.get_template('show.html')
        self.response.write(template.render(template_values))


class EditPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        user = users.get_current_user()
        name = self.request.get('name')
        key = ndb.Key('GPU', name)
        template_values = {'user': user, 'gpu': key.get()}
        template = JINJA_ENVIRONMENT.get_template('edit.html')
        self.response.write(template.render(template_values))

    def post(self):

        message, redirect = self.update_gpu(self.request)

        template_values = {
            'message': message,
            'redirect': redirect,
        }
        template = JINJA_ENVIRONMENT.get_template('message.html')
        self.response.write(template.render(template_values))

    def update_gpu(self, req):
        name = self.request.get('name')
        key = ndb.Key('GPU', name)
        gpu = key.get()

        if gpu:
            gpu.manufacturer = self.request.get('mfg')
            gpu.dateIssued = datetime.datetime.strptime(self.request.get('date'), '%Y-%m-%d')

            gpu.geometryShaderhader = self.request.get('geo-sh').lower() == 'on'
            gpu.tesselationShader = self.request.get('tsl-sh').lower() == 'on'
            gpu.ShaderInt16 = self.request.get('sh-16').lower() == 'on'
            gpu.sparseBinding = self.request.get('sp-bind').lower() == 'on'
            gpu.textureCompressionETC2 = self.request.get('tc-etc2').lower() == 'on'
            gpu.vertexPipelineStoresAndAtomics = self.request.get('vpsa').lower() == 'on'

            gpu.put()

            return 'GPU entry successfully updated', '/show?name=' + name

        else:
            return 'ERROR! GPU name not present in the system', '/show?name=' + name

class ComparePage(webapp2.RequestHandler):
    def post(self):
        self.response.headers['Content-Type'] = 'text/html'
        user = users.get_current_user()
        print()
        print()
        name1 =self.request.POST.keys()[0]
        key1 = ndb.Key('GPU', name1)
        name2 = self.request.POST.keys()[1]
        key2 = ndb.Key('GPU', name2)
        template_values = {'user': user, 'gpu1': key1.get(), 'gpu2':key2.get()}
        template = JINJA_ENVIRONMENT.get_template('compare.html')
        self.response.write(template.render(template_values))


app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/show', ShowPage),
    ('/edit', EditPage),
    ('/compare', ComparePage),
], debug=True)
