from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('privacy_and_legal/terms_and_conditions/', views.terms_and_conditions, name='terms_and_conditions'),
    path('pricing/', views.pricing, name='pricing'),
    path('about/', views.about, name='about'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('verify-email/', views.verify_email, name='verify_email'),
    path('forget-password/', views.forget_password, name='forget_password'),
    path('signup/', views.signup, name='signup'),
    path('forget-password/', views.forget_password, name='forget_password'),
    path('contact/', views.contact, name='contact'),
    path('privacy-and-legal/data-privacy/', views.data_privacy_view, name='data_privacy_view'),

    path('owner_profile/<str:owner_id>', views.owner_profile, name='owner_profile'),
    path('owner_profile/<str:owner_id>/surveys', views.view_owner_survey_requests, name='view_owner_survey_requests'),
    path('owner/<str:owner_id>/buy-subscription/<str:subscription_type>',
         views.buy_subscription_view, name='buy_subscription_view'),

    #path('owner/<str:owner_id>/buy-subscription/<str:subscription_type>',
    #     views.buy_subscription_view, name='buy_subscription_view'),

    path('subscription/<str:owner_id>', views.subscription_view, name='subscription_view'),
    path('my_settings/', views.my_settings, name='my_settings'),
    path('vessel_profile/<str:owner_id>/<str:vessel_id>', views.vessel_profile, name='vessel_profile'),
    path('vessel_registration/<str:owner_id>', views.vessel_registration, name='vessel_registration'),
    path('vessel_profile/<str:vessel_id>/in_progress_surveys', views.surveys_in_progress_view, name='surveys_in_progress_view'),

    path('surveys/condition-survey/<str:owner_id>/<str:vessel_id>/<str:survey_id>', views.generate_condition_survey_view, name='generate_condition_survey_view'),
    path('surveys/condition-survey/<str:survey_id>/<str:owner_id>/<str:vessel_id>/take-photo/<str:vessel_part>/<str:vessel_subpart>',
         views.take_survey_photo_view, name='take_survey_photo_view'),
    path('surveys/condition-survey/<str:survey_id>/<str:owner_id>/<str:vessel_id>/take-photo/<str:vessel_part>/<str:vessel_subpart>/image_preview',
         views.vessel_part_subpart_image_preview, name='vessel_part_subpart_image_preview'),

    path('surveys/condition-survey/<str:owner_id>/<str:vessel_id>/<str:survey_id>/<str:vessel_part>/<str:vessel_subpart>/submit-photos',
         views.submit_photos, name='submit_photos'),

    path('surveys/submit-survey/<str:owner_id>/<str:vessel_id>//<str:survey_id>', views.submit_survey, name='submit_survey'),

    path('surveys/summary/<str:owner_id>/<str:survey_id>',
         views.view_owner_survey_request_summary, name='view_owner_survey_request_summary'),
    path('surveys/summary-part/<str:survey_id>/<str:vessel_part>', views.survey_part_summary_view, name='survey_part_summary_view'),

    path('surveys/downlaods/<str:owner_id>/<str:survey_id>',
         views.download_survey, name='download_survey'),

    path('surveys/<str:owner_id>/<str:vessel_id>', views.generate_survey_view, name='generate_survey_view'),


    path('surveyor_profile/<str:surveyor_id>', views.surveyor_profile, name='surveyor_profile'),
    path('surveyor_profile/<str:surveyor_id>/surveys/<str:survey_id>',
         views.surveyor_survey_view, name='surveyor_survey_view'),
    path('surveyor_profile/<str:surveyor_id>/surveys/<str:survey_id>/<str:vessel_part>/<str:vessel_subpart>',
         views.surveyor_vessel_part_subpart_images, name='surveyor_vessel_part_subpart_images'),

path('surveyor_profile/<str:surveyor_id>/surveys/<str:survey_id>/<str:vessel_part>/<str:vessel_subpart>/view-photo/<str:img_url>',
         views.surveyor_photo_view, name='surveyor_photo_view')


]
