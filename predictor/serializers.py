from rest_framework import serializers

class SalaryInputSerializer(serializers.Serializer):
    feature1 = serializers.FloatField()
    feature2 = serializers.FloatField()
    feature3 = serializers.FloatField()
    feature4 = serializers.FloatField()
    feature5 = serializers.FloatField()
    feature6 = serializers.FloatField()
    feature7 = serializers.FloatField()
    feature8 = serializers.FloatField()
    feature9 = serializers.FloatField()
    feature10 = serializers.CharField()
