from django.urls import path
from . import agent_views

urlpatterns = [
    # ----- Login/Signup ------
    path('', agent_views.login_agent, name="agent_home"),
    path('signup/', agent_views.signup_agent, name="agent_signup"),
    path('logout/', agent_views.logout_agent, name="agent_logout"),
    path('dashboard/', agent_views.dashboard, name="agent_dashboard"),
    path('manufacturer/register', agent_views.register_manufacturer, name="manu_register"),
    path('productlist/<int:manufacturer_id>/', agent_views.product_list, name="manu_prodlist"),
    path('addproduct/<int:manufacturer_id>/', agent_views.add_product, name="manu_addprod"),
    path('orderlist/<int:manufacturer_id>/', agent_views.order_list, name="manu_orderlist"),
    # path('manu/', agent_views.manufacturer),
        
]