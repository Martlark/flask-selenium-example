import os
import random
import string
import threading
import time
import unittest

from selenium import webdriver
from app import app

# configuration
# https://www.kenst.com/2019/02/installing-chromedriver-on-windows/
os.environ['PATH'] += os.pathsep + r'C:\ProgramData\chocolatey\lib\chromedriver\tools'
port = 5005
host_name = f'http://localhost:{port}'


class SeleniumTest(unittest.TestCase):
    driver = None

    @classmethod
    def setUpClass(cls) -> None:
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        try:
            cls.driver = webdriver.Chrome(options=options)
        except Exception as e:
            print(f'ERROR: {e}')

        if cls.driver:
            # create client
            cls.app = app
            cls.app.testing = True
            cls.app_context = cls.app.app_context()
            cls.app_context.push()

            # start the Flask server in a thread
            threading.Thread(target=cls.app.run, kwargs=dict(port=port)).start()

            # give the server a second to ensure it is up
            time.sleep(3)

    @classmethod
    def tearDownClass(cls):
        if cls.driver:
            # stop the flask server and the browser
            cls.driver.get(f'{host_name}/shutdown')
            cls.driver.stop_client()
            cls.driver.quit()

            # destroy database
            # remove application context
            cls.app_context.pop()

    def setUp(self):
        if not self.driver:
            self.skipTest('Web browser not available')

    def tearDown(self):
        pass

    def set_text(self, item_id: str, text: str = ''):
        """
        clear and set the input element identified by the item_id

        :param item_id: id of item to set text
        :param text:
        """
        input = self.driver.find_element_by_id(item_id)
        input.clear()
        input.send_keys(text)

    def assertDisplayed(self, item: object):
        """
        assert that item is displayed.

        :param item: id or a selenium element.  if id is str tries to find by id
        """
        if type(item) == str:
            item = self.driver.find_element_by_id(item)
        self.assertTrue(item.is_displayed(), 'Item is not displayed')

    def assertHidden(self, item: object):
        """
        assert that item is hidden.

        :param item: id or a selenium element.  if id is str tries to find by id
        """
        if type(item) == str:
            item = self.driver.find_element_by_id(item)
        self.assertFalse(item.is_displayed(), 'Item is not hidden')

    @staticmethod
    def random_string(length: int = 20):
        return ''.join([random.choice(string.ascii_letters) for r in range(length)])


class PageIndex(SeleniumTest):

    def assertMessage(self, message):
        self.assertEqual(message, self.driver.find_element_by_id(f'message').text)

    def setUp(self):
        self.initial_list_count = 5

    def test_load(self):
        self.driver.get(f'{host_name}/')

        self.assertTrue(self.driver.find_elements_by_tag_name('header'))
        main_content = self.driver.find_element_by_id('content-list')
        self.assertTrue(main_content)
        items = main_content.find_elements_by_tag_name('li')
        self.assertEqual(len(items), 5)

    def test_remove_item(self):
        self.driver.get(f'{host_name}/')
        node_id = 1
        self.assertTrue(self.driver.find_elements_by_tag_name('header'))
        li_node = self.driver.find_element_by_id(f'li-node-{node_id}')
        self.assertTrue(li_node)
        button = li_node.find_elements_by_tag_name('button')[1]
        button.click()
        self.assertMessage(f'removed: {node_id}', )

    def test_update_item(self):
        self.driver.get(f'{host_name}/')
        node_id = 1
        self.assertTrue(self.driver.find_elements_by_tag_name('header'))
        li_node = self.driver.find_element_by_id(f'li-node-{node_id}')
        self.assertTrue(li_node)
        new_first = self.random_string()
        new_last = self.random_string()
        first = li_node.find_element_by_css_selector('input[name=first]')
        last = li_node.find_element_by_css_selector('input[name=last]')
        first.clear()
        first.send_keys(new_first)
        last.clear()
        last.send_keys(new_last)
        button = li_node.find_elements_by_tag_name('button')[0]
        button.click()
        li_node = self.driver.find_element_by_id(f'li-node-{node_id}')
        li_text = li_node.find_elements_by_tag_name('span')[0]
        self.assertEqual(li_text.text, f'{new_first} {new_last}')
        self.assertMessage(f'updated: {node_id}')

    def test_delete_all(self):
        self.driver.get(f'{host_name}/')
        ul = self.driver.find_element_by_id('content-list')
        self.assertTrue(ul)
        li_list = ul.find_elements_by_tag_name('li')
        existing_count = len(li_list)
        self.assertEqual(self.initial_list_count, len(li_list))
        button = self.driver.find_element_by_id(f'deleteAll')
        self.assertTrue(button)
        button.click()
        li_list = ul.find_elements_by_tag_name('li')
        self.assertEqual(0, len(li_list))
        self.assertMessage(f'removed: {existing_count}', )
        self.assertFalse(button.is_displayed())

    def test_delete_all_add(self):
        self.driver.get(f'{host_name}/')
        ul = self.driver.find_element_by_id('content-list')
        button = self.driver.find_element_by_id(f'deleteAll')
        button.click()
        self.assertFalse(button.is_displayed())
        self.driver.find_element_by_id(f'add').click()
        self.set_text('new_first', self.random_string())
        self.set_text('new_last', self.random_string())
        submit = self.driver.find_element_by_id(f'submit')
        submit.click()
        self.assertTrue(button.is_displayed())

    def test_add(self):
        self.driver.get(f'{host_name}/')

        ul = self.driver.find_element_by_id('content-list')
        self.assertTrue(ul)
        li_list = ul.find_elements_by_tag_name('li')
        li_count = len(li_list)
        self.driver.find_element_by_id(f'add').click()
        self.assertDisplayed('form')
        self.assertHidden('add')
        first = self.random_string()
        last = self.random_string()
        self.set_text(f'new_first')
        self.set_text(f'new_last')
        submit = self.driver.find_element_by_id(f'submit')
        submit.click()
        self.assertMessage(f'first name required')
        self.assertEqual(len(ul.find_elements_by_tag_name('li')), li_count)
        self.set_text('new_first', first)
        submit.click()
        self.assertMessage(f'last name required')
        self.assertEqual(len(ul.find_elements_by_tag_name('li')), li_count)
        self.set_text('new_last', last)
        submit.click()
        li_list = ul.find_elements_by_tag_name('li')
        self.assertEqual(len(li_list), li_count + 1)
        self.assertMessage(f'added')
        self.assertHidden('form')
        self.assertDisplayed('add')
        li_last = ul.find_element_by_css_selector('li:last-child span')
        self.assertEqual(f'{first} {last}', li_last.text)

    def test_add_cancel(self):
        self.driver.get(f'{host_name}/')

        ul = self.driver.find_element_by_id('content-list')
        self.assertTrue(ul)
        li_list = ul.find_elements_by_tag_name('li')
        li_count = len(li_list)
        self.driver.find_element_by_id(f'add').click()
        self.assertDisplayed('form')
        self.assertHidden('add')
        self.driver.find_element_by_id(f'cancel').click()
        li_list = ul.find_elements_by_tag_name('li')
        self.assertEqual(len(li_list), li_count)
        self.assertHidden('form')


if __name__ == '__main__':
    unittest.main()
