    from django.db import models

    # Create your models here.
    class Pizza(models.Model):
        SIZES = [('S', 'Small'), ('M', 'Medium'), ('L', 'Large')]
        name = models.CharField(max_length=100)
        description = models.TextField()
        price = models.DecimalField(max_digits=6, decimal_places=2)
        size = models.CharField(max_length=1, choices=SIZES, default='M')
        image_url = models.URLField(blank=True)
        is_available = models.BooleanField(default=True)
        order = models.IntegerField(default=0)
        
    class Meta:
            ordering = ['order']

        def __str__(self):
            return f"{self.name} ({self.get_size_display()})"


    class Order(models.Model):
        STATUS = [('pending', 'Pending'), ('making', 'Making'), ('delivered', 'Delivered')]
        customer_name = models.CharField(max_length=100)
        customer_email = models.EmailField()
        pizzas = models.ManyToManyField(Pizza, through='OrderItem')
        status = models.CharField(max_length=20, choices=STATUS, default='pending')
        created_at = models.DateTimeField(auto_now_add=True)
        total = models.DecimalField(max_digits=8, decimal_places=2, default=0)

        def __str__(self):
            return f"Order #{self.id} - {self.customer_name}"


    class OrderItem(models.Model):
        order = models.ForeignKey(Order, on_delete=models.CASCADE)
        pizza = models.ForeignKey(Pizza, on_delete=models.CASCADE)
        quantity = models.PositiveIntegerField(default=1)