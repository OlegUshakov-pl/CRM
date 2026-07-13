from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse, resolve


class URLResolutionTest(TestCase):
    """Test that all URLs resolve correctly."""

    def test_core_dashboard_resolves(self):
        url = reverse('core:dashboard')
        self.assertEqual(url, '/')

    def test_core_search_resolves(self):
        url = reverse('core:search')
        self.assertEqual(url, '/search/')

    def test_core_help_resolves(self):
        url = reverse('core:help')
        self.assertEqual(url, '/help/')

    def test_core_settings_resolves(self):
        url = reverse('core:settings_page')
        self.assertEqual(url, '/settings/')

    def test_accounts_login_resolves(self):
        url = reverse('accounts:login')
        self.assertEqual(url, '/accounts/login/')

    def test_accounts_logout_resolves(self):
        url = reverse('accounts:logout')
        self.assertEqual(url, '/accounts/logout/')

    def test_accounts_profile_resolves(self):
        url = reverse('accounts:profile')
        self.assertEqual(url, '/accounts/profile/')

    def test_contacts_list_resolves(self):
        url = reverse('contacts:contact_list')
        self.assertEqual(url, '/contacts/')

    def test_contacts_create_resolves(self):
        url = reverse('contacts:contact_create')
        self.assertEqual(url, '/contacts/create/')

    def test_tasks_list_resolves(self):
        url = reverse('tasks:list')
        self.assertEqual(url, '/tasks/')

    def test_tasks_create_resolves(self):
        url = reverse('tasks:create')
        self.assertEqual(url, '/tasks/create/')

    def test_projects_list_resolves(self):
        url = reverse('projects:list')
        self.assertEqual(url, '/projects/')

    def test_projects_create_resolves(self):
        url = reverse('projects:create')
        self.assertEqual(url, '/projects/create/')

    def test_projects_import_resolves(self):
        url = reverse('projects:import_page')
        self.assertEqual(url, '/projects/import/')

    def test_notes_list_resolves(self):
        url = reverse('notes:list')
        self.assertEqual(url, '/notes/')

    def test_notes_create_resolves(self):
        url = reverse('notes:create')
        self.assertEqual(url, '/notes/create/')

    def test_companies_list_resolves(self):
        url = reverse('companies:company_list')
        self.assertEqual(url, '/companies/')

    def test_companies_create_resolves(self):
        url = reverse('companies:company_create')
        self.assertEqual(url, '/companies/create/')

    def test_documents_list_resolves(self):
        url = reverse('documents:list')
        self.assertEqual(url, '/documents/')

    def test_documents_categories_resolves(self):
        url = reverse('documents:category_list')
        self.assertEqual(url, '/documents/categories/')

    def test_documents_projects_resolves(self):
        url = reverse('documents:projects')
        self.assertEqual(url, '/documents/projects/')

    def test_materials_main_resolves(self):
        url = reverse('materials:main')
        self.assertEqual(url, '/materials/')

    def test_materials_common_resolves(self):
        url = reverse('materials:common')
        self.assertEqual(url, '/materials/common/')

    def test_materials_categories_resolves(self):
        url = reverse('materials:category_list')
        self.assertEqual(url, '/materials/categories/')

    def test_parts_list_resolves(self):
        url = reverse('parts:list')
        self.assertEqual(url, '/parts/')

    def test_parts_projects_resolves(self):
        url = reverse('parts:projects')
        self.assertEqual(url, '/parts/projects/')

    def test_deals_list_resolves(self):
        url = reverse('generators:list')
        self.assertEqual(url, '/deals/')

    def test_deals_create_resolves(self):
        url = reverse('generators:create')
        self.assertEqual(url, '/deals/create/')

    def test_calendar_resolves(self):
        url = reverse('calendar_app:view')
        self.assertEqual(url, '/calendar/')

    def test_assistant_resolves(self):
        url = reverse('assistant:chat')
        self.assertEqual(url, '/assistant/chat/send/')

    def test_library_resolves(self):
        url = reverse('library:list')
        self.assertEqual(url, '/library/')


class AuthRequiredPageAccessTest(TestCase):
    """Test that all pages redirect to login when not authenticated."""

    def setUp(self):
        self.client = Client()

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse('core:dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)

    def test_search_requires_login(self):
        response = self.client.get(reverse('core:search'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)

    def test_help_requires_login(self):
        response = self.client.get(reverse('core:help'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)

    def test_settings_requires_login(self):
        response = self.client.get(reverse('core:settings_page'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)

    def test_contacts_list_requires_login(self):
        response = self.client.get(reverse('contacts:contact_list'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)

    def test_tasks_list_requires_login(self):
        response = self.client.get(reverse('tasks:list'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)

    def test_projects_list_requires_login(self):
        response = self.client.get(reverse('projects:list'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)

    def test_notes_list_requires_login(self):
        response = self.client.get(reverse('notes:list'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)

    def test_companies_list_requires_login(self):
        response = self.client.get(reverse('companies:company_list'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)

    def test_documents_list_requires_login(self):
        response = self.client.get(reverse('documents:list'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)

    def test_materials_main_requires_login(self):
        response = self.client.get(reverse('materials:main'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)

    def test_parts_list_requires_login(self):
        response = self.client.get(reverse('parts:list'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)

    def test_deals_list_requires_login(self):
        response = self.client.get(reverse('generators:list'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)

    def test_calendar_requires_login(self):
        response = self.client.get(reverse('calendar_app:view'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)

    def test_assistant_requires_login(self):
        response = self.client.get(reverse('assistant:chat'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)

    def test_library_requires_login(self):
        response = self.client.get(reverse('library:list'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)


class AuthenticatedPageAccessTest(TestCase):
    """Test that authenticated users can access pages."""

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client = Client()
        self.client.login(username='testuser', password='testpass')

    def test_dashboard_accessible(self):
        response = self.client.get(reverse('core:dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_search_accessible(self):
        response = self.client.get(reverse('core:search'))
        self.assertEqual(response.status_code, 200)

    def test_help_accessible(self):
        response = self.client.get(reverse('core:help'))
        self.assertEqual(response.status_code, 200)

    def test_settings_accessible(self):
        response = self.client.get(reverse('core:settings_page'))
        self.assertEqual(response.status_code, 200)

    def test_contacts_list_accessible(self):
        response = self.client.get(reverse('contacts:contact_list'))
        self.assertEqual(response.status_code, 200)

    def test_contacts_create_accessible(self):
        response = self.client.get(reverse('contacts:contact_create'))
        self.assertEqual(response.status_code, 200)

    def test_contacts_create_slide_accessible(self):
        response = self.client.get(reverse('contacts:contact_create_slide'))
        self.assertEqual(response.status_code, 200)

    def test_tasks_list_accessible(self):
        response = self.client.get(reverse('tasks:list'))
        self.assertEqual(response.status_code, 200)

    def test_tasks_create_accessible(self):
        response = self.client.get(reverse('tasks:create'))
        self.assertEqual(response.status_code, 200)

    def test_tasks_create_slide_accessible(self):
        response = self.client.get(reverse('tasks:create_slide'))
        self.assertEqual(response.status_code, 200)

    def test_projects_list_accessible(self):
        response = self.client.get(reverse('projects:list'))
        self.assertEqual(response.status_code, 200)

    def test_projects_create_accessible(self):
        response = self.client.get(reverse('projects:create'))
        self.assertEqual(response.status_code, 200)

    def test_projects_create_slide_accessible(self):
        response = self.client.get(reverse('projects:create_slide'))
        self.assertEqual(response.status_code, 200)

    def test_projects_import_accessible(self):
        response = self.client.get(reverse('projects:import_page'))
        self.assertEqual(response.status_code, 200)

    def test_notes_list_accessible(self):
        response = self.client.get(reverse('notes:list'))
        self.assertEqual(response.status_code, 200)

    def test_notes_create_accessible(self):
        response = self.client.get(reverse('notes:create'))
        self.assertEqual(response.status_code, 200)

    def test_notes_create_slide_accessible(self):
        response = self.client.get(reverse('notes:create_slide'))
        self.assertEqual(response.status_code, 200)

    def test_companies_list_accessible(self):
        response = self.client.get(reverse('companies:company_list'))
        self.assertEqual(response.status_code, 200)

    def test_companies_create_accessible(self):
        response = self.client.get(reverse('companies:company_create'))
        self.assertEqual(response.status_code, 200)

    def test_companies_create_slide_accessible(self):
        response = self.client.get(reverse('companies:company_create_slide'))
        self.assertEqual(response.status_code, 200)

    def test_documents_list_accessible(self):
        response = self.client.get(reverse('documents:list'))
        self.assertEqual(response.status_code, 200)

    def test_documents_categories_accessible(self):
        response = self.client.get(reverse('documents:category_list'))
        self.assertEqual(response.status_code, 200)

    def test_documents_projects_accessible(self):
        response = self.client.get(reverse('documents:projects'))
        self.assertEqual(response.status_code, 200)

    def test_documents_common_latest_accessible(self):
        response = self.client.get(reverse('documents:common_latest'))
        self.assertEqual(response.status_code, 200)

    def test_materials_main_accessible(self):
        response = self.client.get(reverse('materials:main'))
        self.assertEqual(response.status_code, 200)

    def test_materials_common_accessible(self):
        response = self.client.get(reverse('materials:common'))
        self.assertEqual(response.status_code, 200)

    def test_materials_common_latest_accessible(self):
        response = self.client.get(reverse('materials:common_latest'))
        self.assertEqual(response.status_code, 200)

    def test_materials_categories_accessible(self):
        response = self.client.get(reverse('materials:category_list'))
        self.assertEqual(response.status_code, 200)

    def test_parts_list_accessible(self):
        response = self.client.get(reverse('parts:list'))
        self.assertEqual(response.status_code, 200)

    def test_parts_projects_accessible(self):
        response = self.client.get(reverse('parts:projects'))
        self.assertEqual(response.status_code, 200)

    def test_parts_model_projects_accessible(self):
        response = self.client.get(reverse('parts:model_projects'))
        self.assertEqual(response.status_code, 200)

    def test_parts_common_latest_accessible(self):
        response = self.client.get(reverse('parts:common_latest'))
        self.assertEqual(response.status_code, 200)

    def test_parts_categories_accessible(self):
        response = self.client.get(reverse('parts:category_list'))
        self.assertEqual(response.status_code, 200)

    def test_deals_list_accessible(self):
        response = self.client.get(reverse('generators:list'))
        self.assertEqual(response.status_code, 200)

    def test_deals_create_accessible(self):
        response = self.client.get(reverse('generators:create'))
        self.assertEqual(response.status_code, 200)

    def test_deals_create_slide_accessible(self):
        response = self.client.get(reverse('generators:create_slide'))
        self.assertEqual(response.status_code, 200)

    def test_calendar_accessible(self):
        response = self.client.get(reverse('calendar_app:view'))
        self.assertEqual(response.status_code, 200)

    def test_assistant_requires_post(self):
        response = self.client.get(reverse('assistant:chat'))
        self.assertEqual(response.status_code, 405)

    def test_library_accessible(self):
        response = self.client.get(reverse('library:list'))
        self.assertEqual(response.status_code, 200)


class DetailPageNavigationTest(TestCase):
    """Test detail/edit pages with actual objects."""

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client = Client()
        self.client.login(username='testuser', password='testpass')

    def test_contact_detail_page(self):
        from contacts.models import Contact
        contact = Contact.objects.create(
            first_name='John', last_name='Doe',
            email='john@test.com', phone='+1234567890',
            created_by=self.user,
        )
        response = self.client.get(reverse('contacts:contact_detail', kwargs={'slug': contact.slug}))
        self.assertEqual(response.status_code, 200)

    def test_contact_edit_page(self):
        from contacts.models import Contact
        contact = Contact.objects.create(
            first_name='John', last_name='Doe',
            email='john@test.com', phone='+1234567890',
            created_by=self.user,
        )
        response = self.client.get(reverse('contacts:contact_edit', kwargs={'slug': contact.slug}))
        self.assertEqual(response.status_code, 200)

    def test_contact_edit_slide_page(self):
        from contacts.models import Contact
        contact = Contact.objects.create(
            first_name='John', last_name='Doe',
            email='john@test.com', phone='+1234567890',
            created_by=self.user,
        )
        response = self.client.get(reverse('contacts:contact_edit_slide', kwargs={'slug': contact.slug}))
        self.assertEqual(response.status_code, 200)

    def test_task_edit_page(self):
        from tasks.models import Task
        task = Task.objects.create(
            title='Test Task', priority='medium',
            status='todo', created_by=self.user,
        )
        response = self.client.get(reverse('tasks:edit', kwargs={'slug': task.slug}))
        self.assertEqual(response.status_code, 200)

    def test_task_edit_slide_page(self):
        from tasks.models import Task
        task = Task.objects.create(
            title='Test Task', priority='medium',
            status='todo', created_by=self.user,
        )
        response = self.client.get(reverse('tasks:edit_slide', kwargs={'slug': task.slug}))
        self.assertEqual(response.status_code, 200)

    def test_project_detail_page(self):
        from projects.models import Project
        project = Project.objects.create(
            name='Test Project', number='001',
            status='planning', created_by=self.user,
        )
        response = self.client.get(reverse('projects:detail', kwargs={'slug': project.slug}))
        self.assertEqual(response.status_code, 200)

    def test_project_edit_page(self):
        from projects.models import Project
        project = Project.objects.create(
            name='Test Project', number='001',
            status='planning', created_by=self.user,
        )
        response = self.client.get(reverse('projects:edit', kwargs={'slug': project.slug}))
        self.assertEqual(response.status_code, 200)

    def test_project_edit_slide_page(self):
        from projects.models import Project
        project = Project.objects.create(
            name='Test Project', number='001',
            status='planning', created_by=self.user,
        )
        response = self.client.get(reverse('projects:edit_slide', kwargs={'slug': project.slug}))
        self.assertEqual(response.status_code, 200)

    def test_note_detail_page(self):
        from notes.models import Note
        note = Note.objects.create(
            title='Test Note', content='Test content',
            created_by=self.user,
        )
        response = self.client.get(reverse('notes:detail', kwargs={'slug': note.slug}))
        self.assertEqual(response.status_code, 200)

    def test_note_edit_page(self):
        from notes.models import Note
        note = Note.objects.create(
            title='Test Note', content='Test content',
            created_by=self.user,
        )
        response = self.client.get(reverse('notes:edit', kwargs={'slug': note.slug}))
        self.assertEqual(response.status_code, 200)

    def test_note_edit_slide_page(self):
        from notes.models import Note
        note = Note.objects.create(
            title='Test Note', content='Test content',
            created_by=self.user,
        )
        response = self.client.get(reverse('notes:edit_slide', kwargs={'slug': note.slug}))
        self.assertEqual(response.status_code, 200)

    def test_company_detail_page(self):
        from companies.models import Company
        company = Company.objects.create(
            name='TestCorp', email='info@testcorp.com',
            created_by=self.user,
        )
        response = self.client.get(reverse('companies:company_detail', kwargs={'slug': company.slug}))
        self.assertEqual(response.status_code, 200)

    def test_company_edit_page(self):
        from companies.models import Company
        company = Company.objects.create(
            name='TestCorp', email='info@testcorp.com',
            created_by=self.user,
        )
        response = self.client.get(reverse('companies:company_edit', kwargs={'slug': company.slug}))
        self.assertEqual(response.status_code, 200)

    def test_company_edit_slide_page(self):
        from companies.models import Company
        company = Company.objects.create(
            name='TestCorp', email='info@testcorp.com',
            created_by=self.user,
        )
        response = self.client.get(reverse('companies:company_edit_slide', kwargs={'slug': company.slug}))
        self.assertEqual(response.status_code, 200)

    def test_deal_detail_page(self):
        from generator.models import Deal
        deal = Deal.objects.create(
            name='Test Deal', value=1000,
            status='open', created_by=self.user,
        )
        response = self.client.get(reverse('generators:detail', kwargs={'slug': deal.slug}))
        self.assertEqual(response.status_code, 200)

    def test_deal_edit_page(self):
        from generator.models import Deal
        deal = Deal.objects.create(
            name='Test Deal', value=1000,
            status='open', created_by=self.user,
        )
        response = self.client.get(reverse('generators:edit', kwargs={'slug': deal.slug}))
        self.assertEqual(response.status_code, 200)

    def test_deal_edit_slide_page(self):
        from generator.models import Deal
        deal = Deal.objects.create(
            name='Test Deal', value=1000,
            status='open', created_by=self.user,
        )
        response = self.client.get(reverse('generators:edit_slide', kwargs={'slug': deal.slug}))
        self.assertEqual(response.status_code, 200)


class NavigationLinksTest(TestCase):
    """Test that navigation links work correctly."""

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client = Client()
        self.client.login(username='testuser', password='testpass')

    def test_dashboard_links_to_projects(self):
        response = self.client.get(reverse('core:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '/projects/')

    def test_dashboard_links_to_tasks(self):
        response = self.client.get(reverse('core:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '/tasks/')

    def test_dashboard_links_to_contacts(self):
        response = self.client.get(reverse('core:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '/contacts/')

    def test_dashboard_links_to_notes(self):
        response = self.client.get(reverse('core:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '/notes/')

    def test_project_list_links_to_create(self):
        response = self.client.get(reverse('projects:list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '/projects/create/')

    def test_task_list_links_to_create(self):
        response = self.client.get(reverse('tasks:list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '/tasks/create/')

    def test_contact_list_links_to_create(self):
        response = self.client.get(reverse('contacts:contact_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '/contacts/create/')

    def test_note_list_links_to_create(self):
        response = self.client.get(reverse('notes:list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '/notes/create/')

    def test_company_list_links_to_create(self):
        response = self.client.get(reverse('companies:company_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '/companies/create/')

    def test_deals_list_links_to_create(self):
        response = self.client.get(reverse('generators:list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '/deals/create/')


class SearchFunctionalityTest(TestCase):
    """Test search functionality across modules."""

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client = Client()
        self.client.login(username='testuser', password='testpass')

    def test_search_empty_query(self):
        response = self.client.get(reverse('core:search'))
        self.assertEqual(response.status_code, 200)

    def test_search_with_query(self):
        response = self.client.get(reverse('core:search') + '?q=test')
        self.assertEqual(response.status_code, 200)

    def test_search_finds_contacts(self):
        from contacts.models import Contact
        Contact.objects.create(
            first_name='TestPerson', last_name='Findme',
            email='find@test.com', phone='+1234567890',
            created_by=self.user,
        )
        response = self.client.get(reverse('core:search') + '?q=TestPerson')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'TestPerson')

    def test_search_finds_projects(self):
        from projects.models import Project
        Project.objects.create(
            name='SearchableProject', number='S001',
            status='planning', created_by=self.user,
        )
        response = self.client.get(reverse('core:search') + '?q=SearchableProject')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'SearchableProject')

    def test_search_finds_tasks(self):
        from tasks.models import Task
        Task.objects.create(
            title='SearchableTask', priority='high',
            status='todo', created_by=self.user,
        )
        response = self.client.get(reverse('core:search') + '?q=SearchableTask')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'SearchableTask')

    def test_search_finds_companies(self):
        from companies.models import Company
        Company.objects.create(
            name='SearchableCorp', email='search@test.com',
            created_by=self.user,
        )
        response = self.client.get(reverse('core:search') + '?q=SearchableCorp')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'SearchableCorp')

    def test_search_finds_notes(self):
        from notes.models import Note
        Note.objects.create(
            title='SearchableNote', content='test content',
            created_by=self.user,
        )
        response = self.client.get(reverse('core:search') + '?q=SearchableNote')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'SearchableNote')


class PaginationTest(TestCase):
    """Test pagination across list views."""

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client = Client()
        self.client.login(username='testuser', password='testpass')

    def test_contacts_pagination(self):
        from contacts.models import Contact
        for i in range(25):
            Contact.objects.create(
                first_name=f'Person{i}', last_name='Test',
                email=f'person{i}@test.com', phone=f'+123456789{i:02d}',
                created_by=self.user,
            )
        response = self.client.get(reverse('contacts:contact_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['contacts'].has_next())

    def test_tasks_pagination(self):
        from tasks.models import Task
        for i in range(25):
            Task.objects.create(
                title=f'Task {i}', priority='medium',
                status='todo', created_by=self.user,
            )
        response = self.client.get(reverse('tasks:list'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['tasks'].has_next())

    def test_projects_pagination(self):
        from projects.models import Project
        for i in range(15):
            Project.objects.create(
                name=f'Project {i}', number=f'P{i:03d}',
                status='planning', created_by=self.user,
            )
        response = self.client.get(reverse('projects:list'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['projects'].has_next())

    def test_notes_pagination(self):
        from notes.models import Note
        for i in range(15):
            Note.objects.create(
                title=f'Note {i}', content=f'content {i}',
                created_by=self.user,
            )
        response = self.client.get(reverse('notes:list'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['notes'].has_next())

    def test_companies_pagination(self):
        from companies.models import Company
        for i in range(15):
            Company.objects.create(
                name=f'Corp {i}', email=f'corp{i}@test.com',
                created_by=self.user,
            )
        response = self.client.get(reverse('companies:company_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['companies'].has_next())


class FilterAndSortTest(TestCase):
    """Test filtering and sorting functionality."""

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client = Client()
        self.client.login(username='testuser', password='testpass')

    def test_tasks_filter_by_status(self):
        from tasks.models import Task
        Task.objects.create(title='Todo Task', priority='medium', status='todo', created_by=self.user)
        Task.objects.create(title='Done Task', priority='medium', status='done', created_by=self.user)
        response = self.client.get(reverse('tasks:list') + '?status=todo')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Todo Task')
        self.assertNotContains(response, 'Done Task')

    def test_tasks_filter_by_priority(self):
        from tasks.models import Task
        Task.objects.create(title='High Task', priority='high', status='todo', created_by=self.user)
        Task.objects.create(title='Low Task', priority='low', status='todo', created_by=self.user)
        response = self.client.get(reverse('tasks:list') + '?priority=high')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'High Task')
        self.assertNotContains(response, 'Low Task')

    def test_tasks_search(self):
        from tasks.models import Task
        Task.objects.create(title='Findable Task', priority='medium', status='todo', created_by=self.user)
        Task.objects.create(title='Other Task', priority='medium', status='todo', created_by=self.user)
        response = self.client.get(reverse('tasks:list') + '?q=Findable')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Findable Task')
        self.assertNotContains(response, 'Other Task')

    def test_projects_filter_by_status(self):
        from projects.models import Project
        Project.objects.create(name='Active Project', number='A001', status='active', created_by=self.user)
        Project.objects.create(name='Planning Project', number='P001', status='planning', created_by=self.user)
        response = self.client.get(reverse('projects:list') + '?status=active')
        self.assertEqual(response.status_code, 200)
        projects_page = response.context['projects']
        active_only = [p.status for p in projects_page]
        self.assertTrue(all(s == 'active' for s in active_only))

    def test_projects_search(self):
        from projects.models import Project
        Project.objects.create(name='Findable Project', number='F001', status='planning', created_by=self.user)
        Project.objects.create(name='Other Project', number='O001', status='planning', created_by=self.user)
        response = self.client.get(reverse('projects:list') + '?q=Findable')
        self.assertEqual(response.status_code, 200)
        projects_page = response.context['projects']
        names = [p.name for p in projects_page]
        self.assertIn('Findable Project', names)
        self.assertNotIn('Other Project', names)

    def test_contacts_search(self):
        from contacts.models import Contact
        Contact.objects.create(first_name='Findable', last_name='Person', email='find@test.com', phone='+1234567890', created_by=self.user)
        Contact.objects.create(first_name='Other', last_name='Person', email='other@test.com', phone='+0987654321', created_by=self.user)
        response = self.client.get(reverse('contacts:contact_list') + '?q=Findable')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Findable')
        self.assertNotContains(response, 'Other Person')

    def test_notes_search(self):
        from notes.models import Note
        Note.objects.create(title='Findable Note', content='test', created_by=self.user)
        Note.objects.create(title='Other Note', content='test', created_by=self.user)
        response = self.client.get(reverse('notes:list') + '?q=Findable')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Findable Note')
        self.assertNotContains(response, 'Other Note')


class HTMXNavigationTest(TestCase):
    """Test HTMX slide-over navigation."""

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client = Client()
        self.client.login(username='testuser', password='testpass')

    def test_task_create_slide_returns_htmx(self):
        response = self.client.get(
            reverse('tasks:create_slide'),
            HTTP_HX_REQUEST='true',
        )
        self.assertEqual(response.status_code, 200)

    def test_task_edit_slide_returns_htmx(self):
        from tasks.models import Task
        task = Task.objects.create(title='Slide Task', priority='medium', status='todo', created_by=self.user)
        response = self.client.get(
            reverse('tasks:edit_slide', kwargs={'slug': task.slug}),
            HTTP_HX_REQUEST='true',
        )
        self.assertEqual(response.status_code, 200)

    def test_project_create_slide_returns_htmx(self):
        response = self.client.get(
            reverse('projects:create_slide'),
            HTTP_HX_REQUEST='true',
        )
        self.assertEqual(response.status_code, 200)

    def test_project_edit_slide_returns_htmx(self):
        from projects.models import Project
        project = Project.objects.create(name='Slide Project', number='SP001', status='planning', created_by=self.user)
        response = self.client.get(
            reverse('projects:edit_slide', kwargs={'slug': project.slug}),
            HTTP_HX_REQUEST='true',
        )
        self.assertEqual(response.status_code, 200)

    def test_contact_create_slide_returns_htmx(self):
        response = self.client.get(
            reverse('contacts:contact_create_slide'),
            HTTP_HX_REQUEST='true',
        )
        self.assertEqual(response.status_code, 200)

    def test_contact_edit_slide_returns_htmx(self):
        from contacts.models import Contact
        contact = Contact.objects.create(first_name='Slide', last_name='Contact', email='slide@test.com', phone='+1234567890', created_by=self.user)
        response = self.client.get(
            reverse('contacts:contact_edit_slide', kwargs={'slug': contact.slug}),
            HTTP_HX_REQUEST='true',
        )
        self.assertEqual(response.status_code, 200)

    def test_note_create_slide_returns_htmx(self):
        response = self.client.get(
            reverse('notes:create_slide'),
            HTTP_HX_REQUEST='true',
        )
        self.assertEqual(response.status_code, 200)

    def test_note_edit_slide_returns_htmx(self):
        from notes.models import Note
        note = Note.objects.create(title='Slide Note', content='test', created_by=self.user)
        response = self.client.get(
            reverse('notes:edit_slide', kwargs={'slug': note.slug}),
            HTTP_HX_REQUEST='true',
        )
        self.assertEqual(response.status_code, 200)

    def test_company_create_slide_returns_htmx(self):
        response = self.client.get(
            reverse('companies:company_create_slide'),
            HTTP_HX_REQUEST='true',
        )
        self.assertEqual(response.status_code, 200)

    def test_company_edit_slide_returns_htmx(self):
        from companies.models import Company
        company = Company.objects.create(name='SlideCorp', email='slide@test.com', created_by=self.user)
        response = self.client.get(
            reverse('companies:company_edit_slide', kwargs={'slug': company.slug}),
            HTTP_HX_REQUEST='true',
        )
        self.assertEqual(response.status_code, 200)

    def test_deal_create_slide_returns_htmx(self):
        response = self.client.get(
            reverse('generators:create_slide'),
            HTTP_HX_REQUEST='true',
        )
        self.assertEqual(response.status_code, 200)

    def test_deal_edit_slide_returns_htmx(self):
        from generator.models import Deal
        deal = Deal.objects.create(name='Slide Deal', value=100, status='open', created_by=self.user)
        response = self.client.get(
            reverse('generators:edit_slide', kwargs={'slug': deal.slug}),
            HTTP_HX_REQUEST='true',
        )
        self.assertEqual(response.status_code, 200)
