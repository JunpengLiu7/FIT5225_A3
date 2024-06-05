from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse, JsonResponse, HttpResponseNotAllowed, HttpResponseBadRequest
import boto3

# Create your views here.
def home(request):
    # Fetch the uploaded image names from the S3 bucket
    s3 = boto3.client('s3',
                      aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                      aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                      region_name=settings.AWS_REGION_NAME)
    bucket_name = settings.AWS_S3_BUCKET_NAME
    image_names = [obj.key for obj in s3.list_objects(Bucket=bucket_name)['Contents']]

    return render(request, 'home.html', {'image_names': image_names})


def image_upload_view(request):
    if request.method == 'POST' and request.FILES['image']:
        image = request.FILES['image']
        s3 = boto3.client('s3',
                          aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                          region_name=settings.AWS_REGION_NAME)

        bucket_name = settings.AWS_S3_BUCKET_NAME
        s3.upload_fileobj(image, bucket_name, image.name)

        return HttpResponse('Image uploaded successfully.')
    return render(request, 'upload.html')
