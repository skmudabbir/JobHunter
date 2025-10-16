# Create the missing template files
mkdir -p frontend/templates/applications

# Create scraper.html
cat > frontend/templates/scraper.html << 'EOF'
{% extends "base.html" %}

{% block title %}Job Scraper{% endblock %}

{% block content %}
<div class="max-w-4xl mx-auto">
    <div class="bg-white rounded-lg shadow">
        <div class="px-6 py-4 border-b border-gray-200">
            <h2 class="text-xl font-semibold text-gray-800">Job Scraper</h2>
            <p class="text-gray-600 mt-1">Configure RSS feeds to automatically scrape job listings</p>
        </div>
        
        <div class="p-6">
            <!-- RSS Feed Configuration -->
            <div class="mb-8">
                <h3 class="text-lg font-semibold text-gray-800 mb-4">RSS Feed Configuration</h3>
                <form hx-post="/jobs/scrape" hx-target="#scraping-results" class="space-y-4">
                    <div>
                        <label for="feed_url" class="block text-sm font-medium text-gray-700 mb-1">
                            RSS Feed URL
                        </label>
                        <input type="url" id="feed_url" name="feed_url" 
                               class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                               placeholder="https://example.com/jobs/rss" required>
                    </div>
                    
                    <div>
                        <label for="keywords" class="block text-sm font-medium text-gray-700 mb-1">
                            Keywords (comma-separated)
                        </label>
                        <input type="text" id="keywords" name="keywords" 
                               class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                               placeholder="python, fastapi, remote">
                    </div>
                    
                    <button type="submit" 
                            class="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors">
                        Start Scraping
                    </button>
                </form>
            </div>

            <!-- Scraping Results -->
            <div id="scraping-results">
                <div class="bg-gray-50 rounded-lg p-6 text-center">
                    <i class="fas fa-search text-gray-300 text-4xl mb-3"></i>
                    <p class="text-gray-500">No scraping results yet.</p>
                    <p class="text-gray-400 text-sm mt-1">Configure an RSS feed and start scraping to see results.</p>
                </div>
            </div>

            <!-- Sample RSS Feeds -->
            <div class="mt-8">
                <h3 class="text-lg font-semibold text-gray-800 mb-4">Sample RSS Feeds</h3>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
                        <h4 class="font-semibold text-blue-800">Indeed</h4>
                        <p class="text-blue-600 text-sm mt-1">https://rss.indeed.com/rss?q=python&l=remote</p>
                    </div>
                    <div class="bg-green-50 border border-green-200 rounded-lg p-4">
                        <h4 class="font-semibold text-green-800">RemoteOK</h4>
                        <p class="text-green-600 text-sm mt-1">https://remoteok.io/remote-dev-jobs.rss</p>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
EOF

# Create resumes.html
cat > frontend/templates/resumes.html << 'EOF'
{% extends "base.html" %}

{% block title %}Resume Manager{% endblock %}

{% block content %}
<div class="max-w-6xl mx-auto">
    <div class="bg-white rounded-lg shadow">
        <div class="px-6 py-4 border-b border-gray-200">
            <h2 class="text-xl font-semibold text-gray-800">Resume Manager</h2>
            <p class="text-gray-600 mt-1">Manage and optimize your resumes for different job applications</p>
        </div>
        
        <div class="p-6">
            <!-- Resume List -->
            <div class="mb-8">
                <div class="flex justify-between items-center mb-4">
                    <h3 class="text-lg font-semibold text-gray-800">Your Resumes</h3>
                    <button class="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors">
                        <i class="fas fa-plus mr-2"></i>Add New Resume
                    </button>
                </div>
                
                {% if resumes %}
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {% for resume in resumes %}
                    <div class="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                        <div class="flex justify-between items-start mb-3">
                            <h4 class="font-semibold text-gray-800">{{ resume.name }}</h4>
                            <span class="bg-green-100 text-green-800 text-xs px-2 py-1 rounded-full">
                                Active
                            </span>
                        </div>
                        <p class="text-gray-600 text-sm mb-3">Created: {{ resume.created_at.strftime('%Y-%m-%d') }}</p>
                        <div class="flex space-x-2">
                            <button class="flex-1 bg-blue-100 text-blue-700 text-sm py-1 rounded hover:bg-blue-200 transition-colors">
                                View
                            </button>
                            <button class="flex-1 bg-green-100 text-green-700 text-sm py-1 rounded hover:bg-green-200 transition-colors">
                                Optimize
                            </button>
                            <button class="flex-1 bg-red-100 text-red-700 text-sm py-1 rounded hover:bg-red-200 transition-colors">
                                Delete
                            </button>
                        </div>
                    </div>
                    {% endfor %}
                </div>
                {% else %}
                <div class="text-center py-8 bg-gray-50 rounded-lg">
                    <i class="fas fa-file-alt text-gray-300 text-4xl mb-3"></i>
                    <p class="text-gray-500">No resumes yet.</p>
                    <p class="text-gray-400 text-sm mt-1">Create your first resume to get started.</p>
                </div>
                {% endif %}
            </div>

            <!-- Resume Optimization -->
            <div class="border-t border-gray-200 pt-6">
                <h3 class="text-lg font-semibold text-gray-800 mb-4">Resume Optimizer</h3>
                <div class="bg-gray-50 rounded-lg p-6">
                    <form hx-post="/resumes/optimize" hx-target="#optimization-results" class="space-y-4">
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                                <label class="block text-sm font-medium text-gray-700 mb-1">
                                    Select Resume
                                </label>
                                <select name="resume_id" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500" required>
                                    <option value="">Choose a resume...</option>
                                    {% for resume in resumes %}
                                    <option value="{{ resume.id }}">{{ resume.name }}</option>
                                    {% endfor %}
                                </select>
                            </div>
                            <div>
                                <label class="block text-sm font-medium text-gray-700 mb-1">
                                    Job Description
                                </label>
                                <textarea name="job_description" rows="3" 
                                          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                          placeholder="Paste the job description here..." required></textarea>
                            </div>
                        </div>
                        <button type="submit" 
                                class="bg-purple-600 text-white px-4 py-2 rounded-md hover:bg-purple-700 transition-colors">
                            <i class="fas fa-magic mr-2"></i>Optimize Resume
                        </button>
                    </form>
                    
                    <div id="optimization-results" class="mt-4">
                        <!-- Optimization results will appear here -->
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
EOF

# Create applications.html (main applications page)
cat > frontend/templates/applications.html << 'EOF'
{% extends "base.html" %}

{% block title %}Applications{% endblock %}

{% block content %}
<div class="max-w-7xl mx-auto">
    <div class="bg-white rounded-lg shadow">
        <div class="px-6 py-4 border-b border-gray-200">
            <h2 class="text-xl font-semibold text-gray-800">Job Applications</h2>
            <p class="text-gray-600 mt-1">Track and manage all your job applications in one place</p>
        </div>
        
        <div class="p-6">
            <!-- Filter buttons -->
            <div class="flex flex-wrap gap-2 mb-6">
                <button hx-get="/applications" hx-target="#applications-table" 
                        class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors">
                    All Applications
                </button>
                <button hx-get="/applications?status=applied" hx-target="#applications-table"
                        class="px-4 py-2 bg-blue-100 text-blue-800 rounded-md hover:bg-blue-200 transition-colors">
                    Applied
                </button>
                <button hx-get="/applications?status=interview" hx-target="#applications-table"
                        class="px-4 py-2 bg-green-100 text-green-800 rounded-md hover:bg-green-200 transition-colors">
                    Interviews
                </button>
                <button hx-get="/applications?status=offer" hx-target="#applications-table"
                        class="px-4 py-2 bg-purple-100 text-purple-800 rounded-md hover:bg-purple-200 transition-colors">
                    Offers
                </button>
                <button hx-get="/applications?status=rejected" hx-target="#applications-table"
                        class="px-4 py-2 bg-red-100 text-red-800 rounded-md hover:bg-red-200 transition-colors">
                    Rejected
                </button>
            </div>

            <!-- Applications table -->
            <div id="applications-table">
                {% include "applications/partial.html" %}
            </div>

            <!-- Add Manual Application -->
            <div class="mt-8 border-t border-gray-200 pt-6">
                <h3 class="text-lg font-semibold text-gray-800 mb-4">Add Manual Application</h3>
                <form class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">Job Title</label>
                        <input type="text" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">Company</label>
                        <input type="text" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">Location</label>
                        <input type="text" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">Status</label>
                        <select class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
                            <option value="saved">Saved</option>
                            <option value="applied">Applied</option>
                            <option value="interview">Interview</option>
                            <option value="offer">Offer</option>
                            <option value="rejected">Rejected</option>
                        </select>
                    </div>
                    <div class="md:col-span-2">
                        <label class="block text-sm font-medium text-gray-700 mb-1">Job Description</label>
                        <textarea rows="3" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"></textarea>
                    </div>
                    <div class="md:col-span-2">
                        <button type="submit" class="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 transition-colors">
                            Add Application
                        </button>
                    </div>
                </form>
            </div>
        </div>
    </div>
</div>
{% endblock %}
EOF

# Update the partial.html to be more complete
cat > frontend/templates/applications/partial.html << 'EOF'
<div class="overflow-x-auto">
    <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
            <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Position</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Company</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Location</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
            </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
            {% for app in applications %}
            <tr class="hover:bg-gray-50">
                <td class="px-6 py-4 whitespace-nowrap">
                    <div class="font-medium text-gray-900">{{ app.title }}</div>
                    <div class="text-sm text-gray-500 truncate max-w-xs">{{ app.description[:100] }}...</div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ app.company }}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ app.location }}</td>
                <td class="px-6 py-4 whitespace-nowrap">
                    <span class="px-2 py-1 text-xs rounded-full 
                        {% if app.status == 'applied' %}bg-blue-100 text-blue-800
                        {% elif app.status == 'interview' %}bg-green-100 text-green-800
                        {% elif app.status == 'offer' %}bg-purple-100 text-purple-800
                        {% elif app.status == 'rejected' %}bg-red-100 text-red-800
                        {% else %}bg-gray-100 text-gray-800{% endif %}">
                        {{ app.status }}
                    </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {{ app.created_at.strftime('%Y-%m-%d') if app.created_at else 'N/A' }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <button hx-post="/applications/create" 
                            hx-include="[name='job_id']" 
                            hx-target="#applications-table"
                            class="text-blue-600 hover:text-blue-900 mr-3">
                        Apply
                    </button>
                    <a href="#" class="text-green-600 hover:text-green-900 mr-3">View</a>
                    <a href="#" class="text-red-600 hover:text-red-900">Delete</a>
                    <input type="hidden" name="job_id" value="{{ app.id }}">
                </td>
            </tr>
            {% else %}
            <tr>
                <td colspan="6" class="px-6 py-8 text-center">
                    <i class="fas fa-inbox text-gray-300 text-4xl mb-3"></i>
                    <p class="text-gray-500">No applications found.</p>
                    <p class="text-gray-400 text-sm mt-1">Try scraping some jobs or add a manual application.</p>
                </td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>
EOF