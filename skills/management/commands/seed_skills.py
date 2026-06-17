from django.core.management.base import BaseCommand
from skills.models import Industry, Category


SKILLS_DATA = [
    {
        "name": "Technology",
        "icon": "laptop",
        "categories": [
            "Web Development",
            "Mobile Development",
            "Data Science and Machine Learning",
            "Artificial Intelligence",
            "Cybersecurity",
            "Cloud Computing",
            "DevOps and Site Reliability",
            "Blockchain and Web3",
            "Software Engineering",
            "Database Administration",
            "UI/UX Design",
            "Game Development",
            "Embedded Systems and IoT",
            "Computer Networking",
            "Quality Assurance and Testing",
        ]
    },
    {
        "name": "Business",
        "icon": "briefcase",
        "categories": [
            "Entrepreneurship and Startups",
            "Project Management",
            "Business Analysis",
            "Product Management",
            "Strategy and Consulting",
            "Operations Management",
            "Supply Chain Management",
            "Business Development",
            "Corporate Finance",
        ]
    },
    {
        "name": "Finance, Accounting and Trading",
        "icon": "chart-bar",
        "categories": [
            "Personal Finance and Investing",
            "Accounting and Bookkeeping",
            "Financial Analysis",
            "Forex Trading",
            "Crypto Trading",
            "Stock Market Investing",
            "Commodities Trading",
            "Options and Futures Trading",
            "Copy Trading and Signal Selling",
            "Trading Psychology",
            "CPA Marketing",
            "Taxation",
            "Audit and Compliance",
            "Insurance",
            "Fintech",
        ]
    },
    {
        "name": "Online Business and E-commerce",
        "icon": "shopping-cart",
        "categories": [
            "Dropshipping",
            "Print on Demand",
            "Amazon FBA",
            "Amazon KDP and Self-Publishing",
            "Etsy and Handmade Business",
            "Shopify Store Building",
            "E-commerce Store Management",
            "Digital Products and Downloads",
            "Selling on Jumia and Konga",
        ]
    },
    {
        "name": "Online Income and Digital Hustle",
        "icon": "currency-dollar",
        "categories": [
            "Affiliate Marketing",
            "YouTube Automation and Faceless Content",
            "Blogging and Niche Sites",
            "Email Marketing for Income",
            "Lead Generation",
            "TikTok and Instagram Monetisation",
            "Newsletter Monetisation",
            "Freelancing and Remote Work",
            "Virtual Assistant Services",
            "Selling Digital Templates",
        ]
    },
    {
        "name": "Creative Arts and Design",
        "icon": "paint-brush",
        "categories": [
            "Graphic Design",
            "Motion Graphics and Animation",
            "Video Editing and Production",
            "Photography",
            "3D Modeling and Rendering",
            "Illustration and Digital Art",
            "Brand Identity Design",
            "Interior Design",
            "Fashion Design",
            "Music Production",
            "Songwriting and Composition",
        ]
    },
    {
        "name": "Marketing and Communication",
        "icon": "megaphone",
        "categories": [
            "Digital Marketing",
            "Social Media Marketing",
            "Content Marketing and Copywriting",
            "Search Engine Optimisation",
            "Email Marketing",
            "Influencer Marketing",
            "Public Relations",
            "Advertising",
            "Market Research and Analytics",
            "Community Management",
        ]
    },
    {
        "name": "Personal Development",
        "icon": "user",
        "categories": [
            "Productivity and Time Management",
            "Leadership and Management",
            "Communication and Public Speaking",
            "Critical Thinking and Problem Solving",
            "Emotional Intelligence",
            "Career Development",
            "Negotiation Skills",
            "Memory and Learning Techniques",
        ]
    },
    {
        "name": "Health and Wellness",
        "icon": "heart",
        "categories": [
            "Nutrition and Dietetics",
            "Fitness and Exercise Science",
            "Mental Health and Psychology",
            "Yoga and Mindfulness",
            "First Aid and Emergency Care",
            "Public Health",
            "Alternative Medicine",
        ]
    },
    {
        "name": "Education and Teaching",
        "icon": "academic-cap",
        "categories": [
            "Curriculum Development",
            "E-learning and Instructional Design",
            "Early Childhood Education",
            "Special Needs Education",
            "Tutoring and Coaching",
            "Educational Technology",
        ]
    },
    {
        "name": "Engineering and Architecture",
        "icon": "cog",
        "categories": [
            "Civil and Structural Engineering",
            "Mechanical Engineering",
            "Electrical Engineering",
            "Chemical Engineering",
            "Petroleum Engineering",
            "Architecture and Urban Design",
            "Environmental Engineering",
            "AutoCAD and Technical Drawing",
        ]
    },
    {
        "name": "Media and Journalism",
        "icon": "newspaper",
        "categories": [
            "Journalism and News Writing",
            "Broadcast Media",
            "Podcast Production",
            "Documentary Filmmaking",
            "Scriptwriting",
            "Radio Production",
            "Media Ethics and Law",
        ]
    },
    {
        "name": "Legal and Compliance",
        "icon": "scale",
        "categories": [
            "Nigerian Business Law",
            "Contract Law",
            "Intellectual Property",
            "Employment Law",
            "Legal Research and Writing",
            "Compliance and Risk Management",
            "Alternative Dispute Resolution",
        ]
    },
    {
        "name": "Agriculture and Environment",
        "icon": "leaf",
        "categories": [
            "Modern Farming Techniques",
            "Agribusiness and Farm Management",
            "Crop Science and Horticulture",
            "Animal Husbandry",
            "Aquaculture and Fisheries",
            "Environmental Management",
            "Climate Change and Sustainability",
            "Food Processing and Safety",
        ]
    },
    {
        "name": "Languages",
        "icon": "translate",
        "categories": [
            "English Language and Writing",
            "French",
            "Yoruba",
            "Igbo",
            "Hausa",
            "Arabic",
            "Mandarin Chinese",
            "Spanish",
            "Translation and Interpretation",
        ]
    },
]


class Command(BaseCommand):
    help = 'Seed industries and skill categories for Dotted Academy'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing skills data before seeding',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing data...')
            Category.objects.all().delete()
            Industry.objects.all().delete()
            self.stdout.write(self.style.WARNING('Existing data cleared.'))

        industry_count = 0
        category_count = 0

        for industry_data in SKILLS_DATA:
            industry, created = Industry.objects.get_or_create(
                name=industry_data['name'],
                defaults={
                    'icon': industry_data['icon'],
                    'is_active': True,
                }
            )

            if created:
                industry_count += 1
                self.stdout.write(f'  Created industry: {industry.name}')
            else:
                self.stdout.write(f'  Skipped (exists): {industry.name}')

            for category_name in industry_data['categories']:
                category, cat_created = Category.objects.get_or_create(
                    industry=industry,
                    name=category_name,
                    defaults={'is_active': True}
                )
                if cat_created:
                    category_count += 1

        self.stdout.write(self.style.SUCCESS(
            f'\nDone! Created {industry_count} industries and {category_count} categories.'
        ))