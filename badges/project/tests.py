from django.test import TestCase

from project import api as project_api


class SimpleTest(TestCase):

    project_values = {
        'badge_uri': '/uri/badge/1',
        'user_uri': '/uri/user/testuser/',
        'title': 'Test Title',
        'image_uri': '/uri/image/1',
        'work_url': 'http://project.org/url',
        'steps': 'Did the test',
        'reflection': 'Will do it earlier and more next time',
        'tags': ['test', 'tdd'],
    }


    def test_create_project(self):
        project = project_api.create_project(**self.project_values)
        attrs = self.project_values.keys()
        attrs += ['id', 'uri']

        for attr in attrs:
            self.assertIn(attr, project)

        for attr, value in self.project_values.items():
            self.assertEqual(project[attr], value)

        project2 = project_api.get_project(project['uri'])
        self.assertEqual(project, project2)


    def test_one_project_per_badge(self):
        project = project_api.create_project(**self.project_values)
        self.assertRaises(Exception, project_api.create_project, kwargs=self.project_values)


    def test_project_feedback_cycle(self):
        project = project_api.create_project(**self.project_values)

        project_feedback = project_api.get_project_feedback(project['uri'])
        self.assertEqual(len(project_feedback), 0)

        project_api.submit_feedback(project['uri'], '/uri/user/expert/', 'Ugly', 'Bad', 'Good')
        project_feedback = project_api.get_project_feedback(project['uri'])
        self.assertEqual(len(project_feedback), 1)
        self.assertIn('good', project_feedback[0]) 
        self.assertIn('bad', project_feedback[0]) 
        self.assertIn('ugly', project_feedback[0]) 
        self.assertIn('expert_uri', project_feedback[0]) 

        project_api.revise_project(project['uri'], 'everything is better now!!')
        project_feedback = project_api.get_project_feedback(project['uri'])
        self.assertEqual(len(project_feedback), 2)

        project_api.submit_feedback(project['uri'], '/uri/user/expert/', 'Ugly', 'Bad', 'Good')

        project_api.revise_project(project['uri'], 'everything is better now, promise!!', work_url='http://mywork.com/new-and-improved')
        project_feedback = project_api.get_project_feedback(project['uri'])
        self.assertEqual(len(project_feedback), 4)
 
        self.assertIn('improvement', project_feedback[1]) 
        self.assertIn('date_created', project_feedback[1]) 
        self.assertNotIn('work_url', project_feedback[1])

        self.assertIn('improvement', project_feedback[3]) 
        self.assertIn('work_url', project_feedback[3])
