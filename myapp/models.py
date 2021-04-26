from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser, BaseUserManager

class MyAccountManager(BaseUserManager):
    use_in_migrations = True
    def create_user(self, email, mobile, name, password=None):
        if not email:
            raise ValueError('Users must have an email address')
        if not mobile:
            raise ValueError('Users must have a mobile no')
        if not name:
            raise ValueError('Users must have a name')

        user = self.model(
            email=self.normalize_email(email),
            mobile=mobile,
            name=name,
        )

        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, mobile, name, password):
        user = self.create_user(
            email=self.normalize_email(email),
            password=password,
            mobile=mobile,
            name=name,
        )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class User(AbstractUser):
    username = None
    email = models.EmailField(verbose_name="email", max_length=60, unique=True)
    mobile = models.CharField(max_length=12, unique=True)
    name = models.CharField(max_length = 100)
    is_agent = models.BooleanField(default=False)
    is_customer = models.BooleanField(default=False)
    date_joined	= models.DateTimeField(verbose_name='date joined', auto_now_add=True)
    last_login = models.DateTimeField(verbose_name='last login', auto_now=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)


    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['mobile', 'name']

    objects = MyAccountManager()

    def __str__(self):
        return self.email

	# For checking permissions. to keep it simple all admin have ALL permissons
    def has_perm(self, perm, obj=None):
        return self.is_admin

	# Does this user have permission to view this app? (ALWAYS YES FOR SIMPLICITY)
    def has_module_perms(self, app_label):
        return True


class Agent(models.Model):
    user_id = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True) 
    pincode = models.CharField(max_length = 6) 
    address = models.CharField(max_length = 300)
    aadhar = models.CharField(max_length = 12) 
    verified = models.BooleanField(default=False)
    image = models.ImageField(upload_to='agent-image/', blank=True, default = "")

    def __str__(self): 
        return self.user_id.name

class Manufacturer(models.Model):
    agent_id = models.ForeignKey('Agent', on_delete=models.CASCADE)
    name = models.CharField(max_length = 100)
    company_name = models.CharField(max_length = 100)
    email = models.CharField(max_length = 100, blank=True) 
    mobile = models.CharField(max_length=12) 
    pincode = models.CharField(max_length = 6) 
    address = models.CharField(max_length = 300)
    aadhar = models.CharField(max_length = 12) 
    verified = models.BooleanField(default=False)
    image = models.ImageField(upload_to='agent-image/', blank=True, default = "")

    def __str__(self): 
        return self.company_name


class Product(models.Model):
    manufacturer_id = models.ForeignKey('Manufacturer', on_delete=models.CASCADE)
    name = models.CharField(max_length = 50)
    category = models.ForeignKey('Category', on_delete=models.SET_DEFAULT, default = "other") 
    quantity = models.IntegerField(default = 1)
    description = models.CharField(max_length = 300)
    price = models.IntegerField()
    image = models.ImageField(upload_to='prod-image/', default = "")

    def __str__(self): 
        return self.name

class Category(models.Model):
    name = models.CharField(max_length = 50)

    def __str__(self): 
        return self.name


class Order(models.Model):
    order_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey('User', on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    shipping =  models.ForeignKey('Shipping_Address', on_delete=models.SET_NULL, null = True)
    transaction_id = models.CharField(null = True, max_length = 50)
    totalamt = models.IntegerField(default=None, null=True)
    trans_mode = models.CharField(max_length=30, default=None, null=True)
    coupon = models.ForeignKey('Coupon_Dis', on_delete=models.PROTECT, default=None, null=True)
    
    # def __str__(self): 
    #     return self.order_id

class Coupon_Dis(models.Model):
    coupon_id = models.AutoField(primary_key=True)
    coupon_code = models.CharField(max_length=50)
    discount_percent = models.PositiveIntegerField(default=0,validators=[MinValueValidator(1),MaxValueValidator(100)])
    
class Order_item(models.Model):
    order_id = models.ForeignKey(Order, on_delete=models.CASCADE)
    prod_id = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default = 1)

    # def __str__(self): 
    #     return self.prod_id

class Shipping_Address(models.Model):
    user_id = models.ForeignKey('User', on_delete=models.CASCADE)
    full_name = models.CharField(max_length = 50)
    mobile = models.CharField(max_length=12) 
    pincode = models.CharField(max_length = 6) 
    address = models.CharField(max_length = 300)
    city = models.CharField(max_length = 100) 
    state = models.CharField(max_length = 100)
    date_added = models.DateTimeField(auto_now_add = True)
