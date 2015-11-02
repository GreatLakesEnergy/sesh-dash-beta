from rest_framework import serializers
from seshdash.models import BoM_Data_Point
from django.contrib.auth.models import User


class BoM_Data_PointSerializer(serializers.ModelSerializer):
    class Meta:
        model = BoM_Data_Point
        owner = serializers.ReadOnlyField(source='owner.username')
        fields = ('id', 'site', 'time', 'soc', 'battery_voltage', 'AC_input', 'AC_output', 'AC_Load_in', 'AC_Load_out', 'inverter_state', 'genset_state', 'relay_state', 'unique_together', 'owner')


class UserSerializer(serializers.ModelSerializer):
    bom_data = serializers.PrimaryKeyRelatedField(many=True, queryset=BoM_Data_Point.objects.all())

    class Meta:
        model = User
        fields = ('id', 'username', 'bom_data')
