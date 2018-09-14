from rest_framework import serializers


class nameGenSerializer(serializers.Serializer):
    language = serializers.CharField(max_length=100, required=True)
    name = serializers.CharField(max_length=200, required=True)
    start_char = serializers.CharField(max_length=1, required=False)