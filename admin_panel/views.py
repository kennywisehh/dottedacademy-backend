from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db.models import Sum, Count
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from accounts.models import User
from courses.models import (
    Course, Module, Lesson, Quiz, Question, Option, Enrollment, CourseReview
)
from subscriptions.models import Plan, Subscription, PaymentTransaction
from universities.models import University, Faculty, Department
from skills.models import Industry, Category
from .permissions import IsAdmin
from .serializers import (
    AdminUserSerializer, AdminUserUpdateSerializer,
    AdminUniversitySerializer, AdminFacultySerializer, AdminDepartmentSerializer,
    AdminIndustrySerializer, AdminCategorySerializer,
    AdminCourseSerializer, AdminModuleSerializer, AdminLessonSerializer,
    AdminQuizSerializer, AdminQuestionSerializer, AdminOptionSerializer,
    AdminReviewSerializer, AdminTransactionSerializer,
)


# ── Dashboard ───────────────────────────────────────────────────────────────

@extend_schema(tags=['Admin - Dashboard'])
class AdminDashboardView(APIView):
    permission_classes = [IsAdmin]

    @extend_schema(
        summary='Get admin dashboard stats',
        responses={200: {
            'type': 'object',
            'properties': {
                'total_students': {'type': 'integer'},
                'total_courses': {'type': 'integer'},
                'total_enrollments': {'type': 'integer'},
                'total_revenue': {'type': 'number'},
                'active_subscriptions': {'type': 'integer'},
                'trial_subscriptions': {'type': 'integer'},
            }
        }}
    )
    def get(self, request):
        total_users = User.objects.filter(role='learner').count()
        total_courses = Course.objects.count()
        total_enrollments = Enrollment.objects.count()
        total_revenue = PaymentTransaction.objects.filter(
            status='success'
        ).aggregate(total=Sum('amount'))['total'] or 0
        active_subscriptions = Subscription.objects.filter(status='active').count()
        trial_subscriptions = Subscription.objects.filter(status='trial').count()

        return Response({
            'total_students': total_users,
            'total_courses': total_courses,
            'total_enrollments': total_enrollments,
            'total_revenue': total_revenue,
            'active_subscriptions': active_subscriptions,
            'trial_subscriptions': trial_subscriptions,
        })


# ── Users ────────────────────────────────────────────────────────────────────

@extend_schema(tags=['Admin - Users'])
class AdminUserListView(APIView):
    permission_classes = [IsAdmin]

    @extend_schema(summary='List all users', responses={200: AdminUserSerializer(many=True)})
    def get(self, request):
        users = User.objects.all().order_by('-date_joined')
        serializer = AdminUserSerializer(users, many=True)
        return Response(serializer.data)


@extend_schema(tags=['Admin - Users'])
class AdminUserDetailView(APIView):
    permission_classes = [IsAdmin]

    @extend_schema(summary='Get user detail', responses={200: AdminUserSerializer})
    def get(self, request, id):
        user = get_object_or_404(User, id=id)
        return Response(AdminUserSerializer(user).data)

    @extend_schema(summary='Update user', request=AdminUserUpdateSerializer, responses={200: AdminUserSerializer})
    def patch(self, request, id):
        user = get_object_or_404(User, id=id)
        serializer = AdminUserUpdateSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(AdminUserSerializer(user).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(summary='Delete user', responses={204: None})
    def delete(self, request, id):
        user = get_object_or_404(User, id=id)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ── Universities ─────────────────────────────────────────────────────────────

@extend_schema(tags=['Admin - Universities'])
class AdminUniversityListView(APIView):
    permission_classes = [IsAdmin]

    @extend_schema(summary='List all universities', responses={200: AdminUniversitySerializer(many=True)})
    def get(self, request):
        universities = University.objects.all()
        return Response(AdminUniversitySerializer(universities, many=True).data)

    @extend_schema(summary='Create university', request=AdminUniversitySerializer, responses={201: AdminUniversitySerializer})
    def post(self, request):
        serializer = AdminUniversitySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=['Admin - Universities'])
class AdminUniversityDetailView(APIView):
    permission_classes = [IsAdmin]

    @extend_schema(summary='Get university detail', responses={200: AdminUniversitySerializer})
    def get(self, request, id):
        university = get_object_or_404(University, id=id)
        return Response(AdminUniversitySerializer(university).data)

    @extend_schema(summary='Update university', request=AdminUniversitySerializer, responses={200: AdminUniversitySerializer})
    def put(self, request, id):
        university = get_object_or_404(University, id=id)
        serializer = AdminUniversitySerializer(university, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(summary='Delete university', responses={204: None})
    def delete(self, request, id):
        university = get_object_or_404(University, id=id)
        university.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(tags=['Admin - Universities'])
class AdminFacultyListView(APIView):
    permission_classes = [IsAdmin]

    @extend_schema(summary='List faculties in a university', responses={200: AdminFacultySerializer(many=True)})
    def get(self, request, university_id):
        university = get_object_or_404(University, id=university_id)
        faculties = Faculty.objects.filter(university=university)
        return Response(AdminFacultySerializer(faculties, many=True).data)

    @extend_schema(summary='Create faculty in a university', request=AdminFacultySerializer, responses={201: AdminFacultySerializer})
    def post(self, request, university_id):
        university = get_object_or_404(University, id=university_id)
        serializer = AdminFacultySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(university=university)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=['Admin - Universities'])
class AdminFacultyDetailView(APIView):
    permission_classes = [IsAdmin]

    @extend_schema(summary='Get faculty detail', responses={200: AdminFacultySerializer})
    def get(self, request, university_id, faculty_id):
        faculty = get_object_or_404(Faculty, id=faculty_id, university__id=university_id)
        return Response(AdminFacultySerializer(faculty).data)

    @extend_schema(summary='Update faculty', request=AdminFacultySerializer, responses={200: AdminFacultySerializer})
    def put(self, request, university_id, faculty_id):
        faculty = get_object_or_404(Faculty, id=faculty_id, university__id=university_id)
        serializer = AdminFacultySerializer(faculty, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(summary='Delete faculty', responses={204: None})
    def delete(self, request, university_id, faculty_id):
        faculty = get_object_or_404(Faculty, id=faculty_id, university__id=university_id)
        faculty.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(tags=['Admin - Universities'])
class AdminDepartmentListView(APIView):
    permission_classes = [IsAdmin]

    @extend_schema(summary='List departments in a faculty', responses={200: AdminDepartmentSerializer(many=True)})
    def get(self, request, university_id, faculty_id):
        faculty = get_object_or_404(Faculty, id=faculty_id, university__id=university_id)
        departments = Department.objects.filter(faculty=faculty)
        return Response(AdminDepartmentSerializer(departments, many=True).data)

    @extend_schema(summary='Create department in a faculty', request=AdminDepartmentSerializer, responses={201: AdminDepartmentSerializer})
    def post(self, request, university_id, faculty_id):
        faculty = get_object_or_404(Faculty, id=faculty_id, university__id=university_id)
        serializer = AdminDepartmentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(faculty=faculty)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=['Admin - Universities'])
class AdminDepartmentDetailView(APIView):
    permission_classes = [IsAdmin]

    @extend_schema(summary='Get department detail', responses={200: AdminDepartmentSerializer})
    def get(self, request, university_id, faculty_id, department_id):
        department = get_object_or_404(Department, id=department_id, faculty__id=faculty_id)
        return Response(AdminDepartmentSerializer(department).data)

    @extend_schema(summary='Update department', request=AdminDepartmentSerializer, responses={200: AdminDepartmentSerializer})
    def put(self, request, university_id, faculty_id, department_id):
        department = get_object_or_404(Department, id=department_id, faculty__id=faculty_id)
        serializer = AdminDepartmentSerializer(department, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(summary='Delete department', responses={204: None})
    def delete(self, request, university_id, faculty_id, department_id):
        department = get_object_or_404(Department, id=department_id, faculty__id=faculty_id)
        department.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ── Skills ────────────────────────────────────────────────────────────────────

@extend_schema(tags=['Admin - Skills'])
class AdminIndustryListView(APIView):
    permission_classes = [IsAdmin]

    @extend_schema(summary='List all industries', responses={200: AdminIndustrySerializer(many=True)})
    def get(self, request):
        industries = Industry.objects.all()
        return Response(AdminIndustrySerializer(industries, many=True).data)

    @extend_schema(summary='Create industry', request=AdminIndustrySerializer, responses={201: AdminIndustrySerializer})
    def post(self, request):
        serializer = AdminIndustrySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=['Admin - Skills'])
class AdminIndustryDetailView(APIView):
    permission_classes = [IsAdmin]

    @extend_schema(summary='Get industry detail', responses={200: AdminIndustrySerializer})
    def get(self, request, id):
        industry = get_object_or_404(Industry, id=id)
        return Response(AdminIndustrySerializer(industry).data)

    @extend_schema(summary='Update industry', request=AdminIndustrySerializer, responses={200: AdminIndustrySerializer})
    def put(self, request, id):
        industry = get_object_or_404(Industry, id=id)
        serializer = AdminIndustrySerializer(industry, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(summary='Delete industry', responses={204: None})
    def delete(self, request, id):
        industry = get_object_or_404(Industry, id=id)
        industry.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(tags=['Admin - Skills'])
class AdminCategoryListView(APIView):
    permission_classes = [IsAdmin]

    @extend_schema(summary='List categories in an industry', responses={200: AdminCategorySerializer(many=True)})
    def get(self, request, industry_id):
        industry = get_object_or_404(Industry, id=industry_id)
        categories = Category.objects.filter(industry=industry)
        return Response(AdminCategorySerializer(categories, many=True).data)

    @extend_schema(summary='Create category in an industry', request=AdminCategorySerializer, responses={201: AdminCategorySerializer})
    def post(self, request, industry_id):
        industry = get_object_or_404(Industry, id=industry_id)
        serializer = AdminCategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(industry=industry)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=['Admin - Skills'])
class AdminCategoryDetailView(APIView):
    permission_classes = [IsAdmin]

    @extend_schema(summary='Get category detail', responses={200: AdminCategorySerializer})
    def get(self, request, industry_id, category_id):
        category = get_object_or_404(Category, id=category_id, industry__id=industry_id)
        return Response(AdminCategorySerializer(category).data)

    @extend_schema(summary='Update category', request=AdminCategorySerializer, responses={200: AdminCategorySerializer})
    def put(self, request, industry_id, category_id):
        category = get_object_or_404(Category, id=category_id, industry__id=industry_id)
        serializer = AdminCategorySerializer(category, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(summary='Delete category', responses={204: None})
    def delete(self, request, industry_id, category_id):
        category = get_object_or_404(Category, id=category_id, industry__id=industry_id)
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ── Courses ───────────────────────────────────────────────────────────────────

@extend_schema(tags=['Admin - Courses'])
class AdminCourseListView(APIView):
    permission_classes = [IsAdmin]

    @extend_schema(summary='List all courses', responses={200: AdminCourseSerializer(many=True)})
    def get(self, request):
        courses = Course.objects.select_related('instructor').all()
        return Response(AdminCourseSerializer(courses, many=True).data)

    @extend_schema(summary='Create course', request=AdminCourseSerializer, responses={201: AdminCourseSerializer})
    def post(self, request):
        serializer = AdminCourseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=['Admin - Courses'])
class AdminCourseDetailView(APIView):
    permission_classes = [IsAdmin]

    @extend_schema(summary='Get course detail', responses={200: AdminCourseSerializer})
    def get(self, request, id):
        course = get_object_or_404(Course, id=id)
        return Response(AdminCourseSerializer(course).data)

    @extend_schema(summary='Update course', request=AdminCourseSerializer, responses={200: AdminCourseSerializer})
    def put(self, request, id):
        course = get_object_or_404(Course, id=id)
        serializer = AdminCourseSerializer(course, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(summary='Delete course', responses={204: None})
    def delete(self, request, id):
        course = get_object_or_404(Course, id=id)
        course.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(tags=['Admin - Courses'])
class AdminModuleListView(APIView):
    permission_classes = [IsAdmin]

    @extend_schema(summary='List modules in a course', responses={200: AdminModuleSerializer(many=True)})
    def get(self, request, course_id):
        course = get_object_or_404(Course, id=course_id)
        modules = Module.objects.filter(course=course)
        return Response(AdminModuleSerializer(modules, many=True).data)

    @extend_schema(summary='Create module in a course', request=AdminModuleSerializer, responses={201: AdminModuleSerializer})
    def post(self, request, course_id):
        course = get_object_or_404(Course, id=course_id)
        serializer = AdminModuleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(course=course)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=['Admin - Courses'])
class AdminModuleDetailView(APIView):
    permission_classes = [IsAdmin]

    @extend_schema(summary='Get module detail', responses={200: AdminModuleSerializer})
    def get(self, request, course_id, module_id):
        module = get_object_or_404(Module, id=module_id, course__id=course_id)
        return Response(AdminModuleSerializer(module).data)

    @extend_schema(summary='Update module', request=AdminModuleSerializer, responses={200: AdminModuleSerializer})
    def put(self, request, course_id, module_id):
        module = get_object_or_404(Module, id=module_id, course__id=course_id)
        serializer = AdminModuleSerializer(module, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(summary='Delete module', responses={204: None})
    def delete(self, request, course_id, module_id):
        module = get_object_or_404(Module, id=module_id, course__id=course_id)
        module.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(tags=['Admin - Courses'])
class AdminLessonListView(APIView):
    permission_classes = [IsAdmin]

    @extend_schema(summary='List lessons in a module', responses={200: AdminLessonSerializer(many=True)})
    def get(self, request, course_id, module_id):
        module = get_object_or_404(Module, id=module_id, course__id=course_id)
        lessons = Lesson.objects.filter(module=module)
        return Response(AdminLessonSerializer(lessons, many=True).data)

    @extend_schema(summary='Create lesson in a module', request=AdminLessonSerializer, responses={201: AdminLessonSerializer})
    def post(self, request, course_id, module_id):
        module = get_object_or_404(Module, id=module_id, course__id=course_id)
        serializer = AdminLessonSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(module=module)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=['Admin - Courses'])
class AdminLessonDetailView(APIView):
    permission_classes = [IsAdmin]

    @extend_schema(summary='Get lesson detail', responses={200: AdminLessonSerializer})
    def get(self, request, course_id, module_id, lesson_id):
        lesson = get_object_or_404(Lesson, id=lesson_id, module__id=module_id)
        return Response(AdminLessonSerializer(lesson).data)

    @extend_schema(summary='Update lesson', request=AdminLessonSerializer, responses={200: AdminLessonSerializer})
    def put(self, request, course_id, module_id, lesson_id):
        lesson = get_object_or_404(Lesson, id=lesson_id, module__id=module_id)
        serializer = AdminLessonSerializer(lesson, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(summary='Delete lesson', responses={204: None})
    def delete(self, request, course_id, module_id, lesson_id):
        lesson = get_object_or_404(Lesson, id=lesson_id, module__id=module_id)
        lesson.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ── Quizzes ───────────────────────────────────────────────────────────────────

@extend_schema(tags=['Admin - Quizzes'])
class AdminQuizView(APIView):
    permission_classes = [IsAdmin]

    @extend_schema(summary='Get quiz for a lesson', responses={200: AdminQuizSerializer})
    def get(self, request, lesson_id):
        lesson = get_object_or_404(Lesson, id=lesson_id)
        quiz = get_object_or_404(Quiz, lesson=lesson)
        return Response(AdminQuizSerializer(quiz).data)

    @extend_schema(summary='Create quiz for a lesson', request=AdminQuizSerializer, responses={201: AdminQuizSerializer})
    def post(self, request, lesson_id):
        lesson = get_object_or_404(Lesson, id=lesson_id)
        if hasattr(lesson, 'quiz'):
            return Response({'detail': 'Quiz already exists for this lesson.'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = AdminQuizSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(lesson=lesson)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(summary='Update quiz for a lesson', request=AdminQuizSerializer, responses={200: AdminQuizSerializer})
    def put(self, request, lesson_id):
        lesson = get_object_or_404(Lesson, id=lesson_id)
        quiz = get_object_or_404(Quiz, lesson=lesson)
        serializer = AdminQuizSerializer(quiz, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(summary='Delete quiz for a lesson', responses={204: None})
    def delete(self, request, lesson_id):
        lesson = get_object_or_404(Lesson, id=lesson_id)
        quiz = get_object_or_404(Quiz, lesson=lesson)
        quiz.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(tags=['Admin - Quizzes'])
class AdminQuestionListView(APIView):
    permission_classes = [IsAdmin]

    @extend_schema(summary='List questions in a quiz', responses={200: AdminQuestionSerializer(many=True)})
    def get(self, request, lesson_id):
        quiz = get_object_or_404(Quiz, lesson__id=lesson_id)
        questions = Question.objects.filter(quiz=quiz)
        return Response(AdminQuestionSerializer(questions, many=True).data)

    @extend_schema(summary='Create question in a quiz', request=AdminQuestionSerializer, responses={201: AdminQuestionSerializer})
    def post(self, request, lesson_id):
        quiz = get_object_or_404(Quiz, lesson__id=lesson_id)
        serializer = AdminQuestionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(quiz=quiz)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=['Admin - Quizzes'])
class AdminQuestionDetailView(APIView):
    permission_classes = [IsAdmin]

    @extend_schema(summary='Get question detail', responses={200: AdminQuestionSerializer})
    def get(self, request, lesson_id, question_id):
        question = get_object_or_404(Question, id=question_id, quiz__lesson__id=lesson_id)
        return Response(AdminQuestionSerializer(question).data)

    @extend_schema(summary='Update question', request=AdminQuestionSerializer, responses={200: AdminQuestionSerializer})
    def put(self, request, lesson_id, question_id):
        question = get_object_or_404(Question, id=question_id, quiz__lesson__id=lesson_id)
        serializer = AdminQuestionSerializer(question, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(summary='Delete question', responses={204: None})
    def delete(self, request, lesson_id, question_id):
        question = get_object_or_404(Question, id=question_id, quiz__lesson__id=lesson_id)
        question.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(tags=['Admin - Quizzes'])
class AdminOptionListView(APIView):
    permission_classes = [IsAdmin]

    @extend_schema(summary='Create option for a question', request=AdminOptionSerializer, responses={201: AdminOptionSerializer})
    def post(self, request, lesson_id, question_id):
        question = get_object_or_404(Question, id=question_id, quiz__lesson__id=lesson_id)
        serializer = AdminOptionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(question=question)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=['Admin - Quizzes'])
class AdminOptionDetailView(APIView):
    permission_classes = [IsAdmin]

    @extend_schema(summary='Update option', request=AdminOptionSerializer, responses={200: AdminOptionSerializer})
    def put(self, request, lesson_id, question_id, option_id):
        option = get_object_or_404(Option, id=option_id, question__id=question_id)
        serializer = AdminOptionSerializer(option, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(summary='Delete option', responses={204: None})
    def delete(self, request, lesson_id, question_id, option_id):
        option = get_object_or_404(Option, id=option_id, question__id=question_id)
        option.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ── Reviews ───────────────────────────────────────────────────────────────────

@extend_schema(tags=['Admin - Reviews'])
class AdminReviewListView(APIView):
    permission_classes = [IsAdmin]

    @extend_schema(summary='List all reviews', responses={200: AdminReviewSerializer(many=True)})
    def get(self, request):
        reviews = CourseReview.objects.select_related('user', 'course').all()
        return Response(AdminReviewSerializer(reviews, many=True).data)


@extend_schema(tags=['Admin - Reviews'])
class AdminReviewDetailView(APIView):
    permission_classes = [IsAdmin]

    @extend_schema(summary='Delete review', responses={204: None})
    def delete(self, request, id):
        review = get_object_or_404(CourseReview, id=id)
        review.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ── Revenue ───────────────────────────────────────────────────────────────────

@extend_schema(tags=['Admin - Revenue'])
class AdminRevenueSummaryView(APIView):
    permission_classes = [IsAdmin]

    @extend_schema(
        summary='Get revenue summary',
        responses={200: {
            'type': 'object',
            'properties': {
                'total_revenue': {'type': 'number'},
                'total_transactions': {'type': 'integer'},
                'by_plan': {'type': 'array', 'items': {'type': 'object'}},
                'by_gateway': {'type': 'array', 'items': {'type': 'object'}},
                'recent_transactions': {'type': 'array', 'items': {'type': 'object'}},
            }
        }}
    )
    def get(self, request):
        transactions = PaymentTransaction.objects.filter(status='success')
        total_revenue = transactions.aggregate(total=Sum('amount'))['total'] or 0
        total_transactions = transactions.count()
        by_plan = transactions.values('plan__name').annotate(
            total=Sum('amount'), count=Count('id')
        )
        by_gateway = transactions.values('gateway').annotate(
            total=Sum('amount'), count=Count('id')
        )
        recent = transactions.order_by('-created_at')[:10]

        return Response({
            'total_revenue': total_revenue,
            'total_transactions': total_transactions,
            'by_plan': list(by_plan),
            'by_gateway': list(by_gateway),
            'recent_transactions': AdminTransactionSerializer(recent, many=True).data,
        })