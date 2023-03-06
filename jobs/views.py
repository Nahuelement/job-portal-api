from django.shortcuts import render
from .models import Job, CandidatesApplied
from django.utils import timezone
from .serializers import JobSerializer, CandidatesAppliedSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Avg, Min, Max, Count
from rest_framework import status
# Create your views here.
from .filters import JobsFilter
from rest_framework.pagination import PageNumberPagination

@api_view(['GET'])
def getAllJobs(request):
    filterset = JobsFilter(request.GET, queryset=Job.objects.all().order_by('-id'))


    count = filterset.qs.count()

    # Pagination
    resPerPage = 3

    paginator = PageNumberPagination()
    paginator.page_size = resPerPage

    queryset = paginator.paginate_queryset(filterset.qs, request)


    serializer = JobSerializer(queryset, many=True)
    return Response({
        "count": count,
        "resPerPage": resPerPage,
        'jobs': serializer.data
        })


@api_view(['GET'])
def getJob(request, pk):
    job = get_object_or_404(Job, id=pk)

    candidate = job.candidatesapplied_set.all().count()

    serializer = JobSerializer(job, many=False)

    return Response({
        'job':serializer.data,
        'candidate' : candidate
        })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def newJob(request):
    request.data['user'] = request.user
    data = request.data

    job = Job.objects.create(**data)

    serializer = JobSerializer(job, many=False)
    return Response(serializer.data)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def updateJob(request, pk):
    job = get_object_or_404(Job, id=pk)

    if job.user != request.user:
        return Response({ 'message': 'No puedes actulizar este trabajo' }, status=status.HTTP_403_FORBIDDEN)

    job.title = request.data['title']
    job.description = request.data['description']
    job.email = request.data['email']
    job.address = request.data['address']
    job.jobType = request.data['jobType']
    job.education = request.data['education']
    job.industry = request.data['industry']
    job.experience = request.data['experience']
    job.salary = request.data['salary']
    job.positions = request.data['positions']
    job.company = request.data['company']

    job.save()

    serializer = JobSerializer(job, many=False)

    return Response(serializer.data)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def deleteJob(request, pk):
    job = get_object_or_404(Job, id=pk)

    if job.user != request.user:
        return Response({ 'message': 'No puedes eliminar este trabajo' }, status=status.HTTP_403_FORBIDDEN)

    job.delete()

    return Response({ 'message': 'Trabajo eliminado.' }, status=status.HTTP_200_OK)


@api_view(['GET'])
def getTopicStats(request, topic):

    args = { 'title__icontains': topic }
    jobs = Job.objects.filter(**args)

    if len(jobs) == 0:
        return Response({ 'message': 'No existen estadisticas de  {topic}'.format(topic=topic) })
    data = JobSerializer(jobs, many=True)

    print(data.data)



    stats = jobs.aggregate(
        total_jobs = Count('title'),
        avg_positions = Avg('positions'),
        avg_salary = Avg('salary'),
        min_salary = Min('salary'),
        max_salary = Max('salary')
    )

    return Response(stats)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def applyJob(request, pk):

    user = request.user
    job = get_object_or_404(Job, id=pk)

    if user.userprofile.resume == '':
        return Response({ 'error': 'Por favor sube el cv primero' }, status=status.HTTP_400_BAD_REQUEST)

    if job.lastDate < timezone.now():
        return Response({ 'error': 'No puedes postular a este trabajo, el tiempo de esta publicacion expiro' }, status=status.HTTP_400_BAD_REQUEST)

    alreadyApplied = job.candidatesapplied_set.filter(user=user).exists()
    print(alreadyApplied)


    if alreadyApplied:
        return Response({'error': 'Ya estas postulando a este trabajo. '}, status=status.HTTP_400_BAD_REQUEST)



    jobApplied = CandidatesApplied.objects.create(
            job = job,
            user = user,
            resume = user.userprofile.resume
        )

    return Response({
            'applied': True,
            'job_id': jobApplied.id
        },
        status=status.HTTP_200_OK
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getCurrentUserAppliedJob(request):
    args = {'user_id': request.user.id}

    jobs = CandidatesApplied.objects.filter(**args)

    serializer = CandidatesAppliedSerializer(jobs, many=True)

    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def isApplied(request, pk):

    user = request.user
    job = get_object_or_404(Job, id=pk)
    applied = job.candidatesapplied_set.filter(user=user).exists()

    return Response({'applied':applied})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getCurrentUserJobs(request):

    args = { 'user': request.user.id }

    jobs = Job.objects.filter(**args)
    serializer = JobSerializer(jobs, many=True)

    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getCandidatesApplied(request, pk):

    user = request.user
    job = get_object_or_404(Job, id=pk)

    if (job.user != user):
        return Response ({'error': 'no puedes ver los candidatos de este trabajo'})


    candidate = job.candidatesapplied_set.all()

    serializer = CandidatesAppliedSerializer(candidate, many=True)

    return Response ({'candidate_jobs' : serializer.data })

