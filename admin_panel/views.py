from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db.models import Sum, Count

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

class AdminDashboardView(APIView):
    permission_classes = [IsAdmin]

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

class AdminUserListView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        users = User.objects.all().order_by('-date_joined')
        serializer = AdminUserSerializer(users, many=True)
        return Response(serializer.data)


class AdminUserDetailView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request, id):
        user = get_object_or_404(User, id=id)
        return Response(AdminUserSerializer(user).data)

    def patch(self, request, id):
        user = get_object_or_404(User, id=id)
        serializer = AdminUserUpdateSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(AdminUserSerializer(user).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        user = get_object_or_404(User, id=id)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ── Universities ─────────────────────────────────────────────────────────────

class AdminUniversityListView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        universities = University.objects.all()
        return Response(AdminUniversitySerializer(universities, many=True).data)

    def post(self, request):
        serializer = AdminUniversitySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AdminUniversityDetailView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request, id):
        university = get_object_or_404(University, id=id)
        return Response(AdminUniversitySerializer(university).data)

    def put(self, request, id):
        university = get_object_or_404(University, id=id)
        serializer = AdminUniversitySerializer(university, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        university = get_object_or_404(University, id=id)
        university.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AdminFacultyListView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request, university_id):
        university = get_object_or_404(University, id=university_id)
        faculties = Faculty.objects.filter(university=university)
        return Response(AdminFacultySerializer(faculties, many=True).data)

    def post(self, request, university_id):
        university = get_object_or_404(University, id=university_id)
        serializer = AdminFacultySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(university=university)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AdminFacultyDetailView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request, university_id, faculty_id):
        faculty = get_object_or_404(Faculty, id=faculty_id, university__id=university_id)
        return Response(AdminFacultySerializer(faculty).data)

    def put(self, request, university_id, faculty_id):
        faculty = get_object_or_404(Faculty, id=faculty_id, university__id=university_id)
        serializer = AdminFacultySerializer(faculty, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, university_id, faculty_id):
        faculty = get_object_or_404(Faculty, id=faculty_id, university__id=university_id)
        faculty.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AdminDepartmentListView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request, university_id, faculty_id):
        faculty = get_object_or_404(Faculty, id=faculty_id, university__id=university_id)
        departments = Department.objects.filter(faculty=faculty)
        return Response(AdminDepartmentSerializer(departments, many=True).data)

    def post(self, request, university_id, faculty_id):
        faculty = get_object_or_404(Faculty, id=faculty_id, university__id=university_id)
        serializer = AdminDepartmentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(faculty=faculty)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AdminDepartmentDetailView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request, university_id, faculty_id, department_id):
        department = get_object_or_404(Department, id=department_id, faculty__id=faculty_id)
        return Response(AdminDepartmentSerializer(department).data)

    def put(self, request, university_id, faculty_id, department_id):
        department = get_object_or_404(Department, id=department_id, faculty__id=faculty_id)
        serializer = AdminDepartmentSerializer(department, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, university_id, faculty_id, department_id):
        department = get_object_or_404(Department, id=department_id, faculty__id=faculty_id)
        department.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ── Skills ────────────────────────────────────────────────────────────────────

class AdminIndustryListView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        industries = Industry.objects.all()
        return Response(AdminIndustrySerializer(industries, many=True).data)

    def post(self, request):
        serializer = AdminIndustrySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AdminIndustryDetailView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request, id):
        industry = get_object_or_404(Industry, id=id)
        return Response(AdminIndustrySerializer(industry).data)

    def put(self, request, id):
        industry = get_object_or_404(Industry, id=id)
        serializer = AdminIndustrySerializer(industry, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        industry = get_object_or_404(Industry, id=id)
        industry.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AdminCategoryListView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request, industry_id):
        industry = get_object_or_404(Industry, id=industry_id)
        categories = Category.objects.filter(industry=industry)
        return Response(AdminCategorySerializer(categories, many=True).data)

    def post(self, request, industry_id):
        industry = get_object_or_404(Industry, id=industry_id)
        serializer = AdminCategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(industry=industry)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AdminCategoryDetailView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request, industry_id, category_id):
        category = get_object_or_404(Category, id=category_id, industry__id=industry_id)
        return Response(AdminCategorySerializer(category).data)

    def put(self, request, industry_id, category_id):
        category = get_object_or_404(Category, id=category_id, industry__id=industry_id)
        serializer = AdminCategorySerializer(category, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, industry_id, category_id):
        category = get_object_or_404(Category, id=category_id, industry__id=industry_id)
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ── Courses ───────────────────────────────────────────────────────────────────

class AdminCourseListView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        courses = Course.objects.select_related('instructor').all()
        return Response(AdminCourseSerializer(courses, many=True).data)

    def post(self, request):
        serializer = AdminCourseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AdminCourseDetailView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request, id):
        course = get_object_or_404(Course, id=id)
        return Response(AdminCourseSerializer(course).data)

    def put(self, request, id):
        course = get_object_or_404(Course, id=id)
        serializer = AdminCourseSerializer(course, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        course = get_object_or_404(Course, id=id)
        course.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AdminModuleListView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request, course_id):
        course = get_object_or_404(Course, id=course_id)
        modules = Module.objects.filter(course=course)
        return Response(AdminModuleSerializer(modules, many=True).data)

    def post(self, request, course_id):
        course = get_object_or_404(Course, id=course_id)
        serializer = AdminModuleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(course=course)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AdminModuleDetailView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request, course_id, module_id):
        module = get_object_or_404(Module, id=module_id, course__id=course_id)
        return Response(AdminModuleSerializer(module).data)

    def put(self, request, course_id, module_id):
        module = get_object_or_404(Module, id=module_id, course__id=course_id)
        serializer = AdminModuleSerializer(module, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, course_id, module_id):
        module = get_object_or_404(Module, id=module_id, course__id=course_id)
        module.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AdminLessonListView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request, course_id, module_id):
        module = get_object_or_404(Module, id=module_id, course__id=course_id)
        lessons = Lesson.objects.filter(module=module)
        return Response(AdminLessonSerializer(lessons, many=True).data)

    def post(self, request, course_id, module_id):
        module = get_object_or_404(Module, id=module_id, course__id=course_id)
        serializer = AdminLessonSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(module=module)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AdminLessonDetailView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request, course_id, module_id, lesson_id):
        lesson = get_object_or_404(Lesson, id=lesson_id, module__id=module_id)
        return Response(AdminLessonSerializer(lesson).data)

    def put(self, request, course_id, module_id, lesson_id):
        lesson = get_object_or_404(Lesson, id=lesson_id, module__id=module_id)
        serializer = AdminLessonSerializer(lesson, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, course_id, module_id, lesson_id):
        lesson = get_object_or_404(Lesson, id=lesson_id, module__id=module_id)
        lesson.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ── Quizzes ───────────────────────────────────────────────────────────────────

class AdminQuizView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request, lesson_id):
        lesson = get_object_or_404(Lesson, id=lesson_id)
        quiz = get_object_or_404(Quiz, lesson=lesson)
        return Response(AdminQuizSerializer(quiz).data)

    def post(self, request, lesson_id):
        lesson = get_object_or_404(Lesson, id=lesson_id)
        if hasattr(lesson, 'quiz'):
            return Response({'detail': 'Quiz already exists for this lesson.'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = AdminQuizSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(lesson=lesson)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, lesson_id):
        lesson = get_object_or_404(Lesson, id=lesson_id)
        quiz = get_object_or_404(Quiz, lesson=lesson)
        serializer = AdminQuizSerializer(quiz, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, lesson_id):
        lesson = get_object_or_404(Lesson, id=lesson_id)
        quiz = get_object_or_404(Quiz, lesson=lesson)
        quiz.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AdminQuestionListView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request, lesson_id):
        quiz = get_object_or_404(Quiz, lesson__id=lesson_id)
        questions = Question.objects.filter(quiz=quiz)
        return Response(AdminQuestionSerializer(questions, many=True).data)

    def post(self, request, lesson_id):
        quiz = get_object_or_404(Quiz, lesson__id=lesson_id)
        serializer = AdminQuestionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(quiz=quiz)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AdminQuestionDetailView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request, lesson_id, question_id):
        question = get_object_or_404(Question, id=question_id, quiz__lesson__id=lesson_id)
        return Response(AdminQuestionSerializer(question).data)

    def put(self, request, lesson_id, question_id):
        question = get_object_or_404(Question, id=question_id, quiz__lesson__id=lesson_id)
        serializer = AdminQuestionSerializer(question, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, lesson_id, question_id):
        question = get_object_or_404(Question, id=question_id, quiz__lesson__id=lesson_id)
        question.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AdminOptionListView(APIView):
    permission_classes = [IsAdmin]

    def post(self, request, lesson_id, question_id):
        question = get_object_or_404(Question, id=question_id, quiz__lesson__id=lesson_id)
        serializer = AdminOptionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(question=question)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AdminOptionDetailView(APIView):
    permission_classes = [IsAdmin]

    def put(self, request, lesson_id, question_id, option_id):
        option = get_object_or_404(Option, id=option_id, question__id=question_id)
        serializer = AdminOptionSerializer(option, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, lesson_id, question_id, option_id):
        option = get_object_or_404(Option, id=option_id, question__id=question_id)
        option.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ── Reviews ───────────────────────────────────────────────────────────────────

class AdminReviewListView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        reviews = CourseReview.objects.select_related('user', 'course').all()
        return Response(AdminReviewSerializer(reviews, many=True).data)


class AdminReviewDetailView(APIView):
    permission_classes = [IsAdmin]

    def delete(self, request, id):
        review = get_object_or_404(CourseReview, id=id)
        review.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ── Revenue ───────────────────────────────────────────────────────────────────

class AdminRevenueSummaryView(APIView):
    permission_classes = [IsAdmin]

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