from django.db import models

class Laboratory(models.Model):
    name = models.CharField(max_length=200)
    lab_type = models.CharField(max_length=50)
    location = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class LabTest(models.Model):
    code = models.CharField(max_length=50)
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=100)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    laboratory = models.ForeignKey(Laboratory, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class LabOrder(models.Model):
    order_number = models.CharField(max_length=50)
    patient = models.ForeignKey('shared.Patient', on_delete=models.CASCADE)
    doctor = models.ForeignKey('shared.Doctor', on_delete=models.CASCADE)
    laboratory = models.ForeignKey(Laboratory, on_delete=models.CASCADE)
    status = models.CharField(max_length=50)
    priority = models.CharField(max_length=50, default='NORMAL')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.order_number

class LabResult(models.Model):
    test = models.ForeignKey(LabTest, on_delete=models.CASCADE)
    order = models.ForeignKey(LabOrder, on_delete=models.CASCADE)
    value = models.CharField(max_length=200)
    unit = models.CharField(max_length=50)
    status = models.CharField(max_length=50)
    result_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.test.name}: {self.value}"