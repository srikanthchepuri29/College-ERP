from rest_framework import serializers
from lms.models import LMSMaterial

class LMSMaterialSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    uploaded_by_name = serializers.SerializerMethodField()

    class Meta:
        model = LMSMaterial
        fields = ['id', 'title', 'description', 'subject', 'subject_name', 'uploaded_by', 'uploaded_by_name', 'file', 'external_link', 'uploaded_at', 'download_count']

    def get_uploaded_by_name(self, obj):
        return f"{obj.uploaded_by.user.first_name} {obj.uploaded_by.user.last_name}"
