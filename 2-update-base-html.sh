# Update the navigation in base.html
cat > frontend/templates/base.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>JobHunter - {% block title %}Job Search Assistant{% endblock %}</title>
    <script src="https://unpkg.com/htmx.org@1.9.6"></script>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
</head>
<body class="bg-gray-50">
    <nav class="bg-blue-600 text-white shadow-lg">
        <div class="max-w-7xl mx-auto px-4">
            <div class="flex justify-between items-center py-4">
                <div class="flex items-center space-x-4">
                    <i class="fas fa-search text-xl"></i>
                    <h1 class="text-xl font-bold">JobHunter</h1>
                </div>
                <div class="flex space-x-6">
                    <a href="/" class="hover:text-blue-200 {% if request.url.path == '/' %}border-b-2{% endif %}">Dashboard</a>
                    <a href="/applications-page" class="hover:text-blue-200">Applications</a>
                    <a href="/resumes" class="hover:text-blue-200">Resumes</a>
                    <a href="/jobs/scrape" class="hover:text-blue-200">Job Scraper</a>
                </div>
            </div>
        </div>
    </nav>

    <main class="max-w-7xl mx-auto px-4 py-8">
        {% block content %}{% endblock %}
    </main>

    <footer class="bg-gray-800 text-white py-8 mt-12">
        <div class="max-w-7xl mx-auto px-4 text-center">
            <p>&copy; 2024 JobHunter. Built with FastAPI, HTMX, and TailwindCSS.</p>
        </div>
    </footer>
</body>
</html>
EOF