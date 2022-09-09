from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('privacy_and_legal/terms_and_conditions/', views.terms_and_conditions, name='terms_and_conditions'),
    path('pricing/', views.pricing, name='pricing'),
    path('about/', views.about, name='about'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout_user, name='logout'),

    path('forget-password/', views.forget_password, name='forget-password'),
    path('signup/', views.signup, name='signup'),

    path('success_password_email/', views.success_password_email_view, name='success-password-reset-email'),

    path('contact/', views.contact, name='contact'),
    path('privacy-and-legal/data-privacy/', views.data_privacy_view, name='data_privacy_view'),
    path('subscription/<str:owner_id>', views.subscription_view, name='subscription_view'),

    path('owner/<str:owner_id>/surveys/condition-survey/<str:survey_id>/view-photo/<str:vessel_part>/<str:survey_part_id>/photo/<str:photo_id>/',
        views.owner_view_photo, name='owner-view-photo'),

    path('owner/<str:owner_id>/verify-email/', views.verify_owner_email, name='verify-owner-email'),

    path('owner/<str:owner_id>/dashboard/', views.owner_profile, name='owner-profile'),

    path('owner/<str:owner_id>/surveys/',
         views.view_owner_survey_requests, name='owner-survey-requests'),

    path('owner/<str:owner_id>/buy-subscription/<str:subscription_type>',
         views.buy_subscription_view, name='buy-subscription'),

    path('owner/<str:owner_id>/my-settings/',
         views.my_settings_view, name='my_settings_view'),

    path('owner/<str:owner_id>/delete-profile/',
         views.delete_owner, name='delete_owner'),

    path('owner/<str:owner_id>/not-valid-subscription/',
         views.not_valid_subscription_view, name='not-valid-subscription'),

    path('owner/<str:owner_id>/vessel-profile/<str:vessel_id>/',
         views.vessel_profile, name='vessel_profile'),

    path('owner/<str:owner_id>/vessel-profile/<str:vessel_id>/surveys/<str:survey_id>/summary/',
         views.view_owner_survey_request_summary, name='view_owner_survey_request_summary'),

    path('owner/<str:owner_id>/vessel-profile/<str:vessel_id>/in-progress-surveys/',
         views.vessel_surveys_in_progress_view, name='vessel-surveys-in-progress'),

    path('owner/<str:owner_id>/vessel-profile/<str:vessel_id>/surveys/<str:survey_id>/delete-survey/',
         views.delete_survey_from_vessel, name='delete-vessel-survey'),

    path('owner/<str:owner_id>/surveys/<str:survey_id>/delete/',
         views.delete_owner_vessel_survey, name='delete-owner-vessel-survey'),

    path('owner/<str:owner_id>/vessel-registration/',
         views.vessel_registration, name='vessel_registration'),

    path('owner/<str:owner_id>/vessel/<str:vessel_id>/surveys/',
         views.generate_survey_view, name='generate-survey'),

    path('owner/<str:owner_id>/vessel/<str:vessel_id>/surveys/condition-survey/<str:survey_id>/',
         views.generate_condition_survey_view, name='generate-condition-survey'),

    #path('owner/<str:owner_id>/vessel/<str:vessel_id>/surveys/condition-survey/<str:survey_id>/submit-survey/',
    #     views.submit_survey, name='submit-survey'),

    path('owner/<str:owner_id>/surveys/condition-survey/<str:survey_id>/<str:vessel_part_id>/vessel-part-survey-parts/',
         views.vessel_part_survey_parts_view, name='vessel-part-survey-parts'),

    path('owner/<str:owner_id>/surveys/condition-survey/<str:survey_id>/<str:vessel_part>/<str:survey_part_id>/image-preview/',
         views.vessel_part_subpart_image_preview, name='vessel-part-subpart-image-preview'),

    path('owner/<str:owner_id>/surveys/condition-survey/<str:survey_id>/take-photo/<str:vessel_part>/<str:survey_part_id>/',
         views.take_survey_photo_view, name='take-survey-photo-view'),


    #path('surveys/condition-survey/<str:owner_id>/<str:vessel_id>/<str:survey_id>/<str:vessel_part>/<str:vessel_subpart>/submit-photos',
    #     views.submit_photos, name='submit_photos'),

    path('surveys/submit-survey/<str:owner_id>/<str:vessel_id>/<str:survey_id>',
         views.submit_survey, name='submit_survey'),


    path('surveys/summary-part/<str:survey_id>/<str:vessel_part>',
         views.survey_part_summary_view, name='survey_part_summary_view'),

    path('surveys/downlaods/<str:owner_id>/<str:survey_id>',
         views.download_survey, name='download_survey'),


    path('surveyor/<str:surveyor_id>/verify-email/', views.verify_surveyor_email, name='verify-surveyor-email'),
    path('surveyor/<str:surveyor_id>/dashboard/', views.surveyor_profile, name='surveyor-profile'),
    path('surveyor/<str:surveyor_id>/my-settings/', views.surveyor_settings_view, name='surveyor-settings'),
    path('surveyor/<str:surveyor_id>/delete-profile/', views.delete_surveyor, name='delete-surveyor'),
    path('surveyor/<str:surveyor_id>/surveys/<str:survey_id>/', views.surveyor_survey_view, name='surveyor-survey-view'),
    path('surveyor/<str:surveyor_id>/surveys/<str:survey_id>/submit/', views.submit_survey_surveyor, name='surveyor-submit-survey'),

    #path('surveyor/<str:surveyor_id>/surveys/<str:survey_id>/<str:vessel_part>/<str:vessel_subpart>',
    #     views.surveyor_vessel_part_subpart_images, name='surveyor-vessel-part-subpart-images'),

    path('surveyor/<str:surveyor_id>/surveys/<str:survey_id>/start-survey/',
         views.surveyor_start_survey_view, name='surveyor-start-survey'),
    path('surveyor/<str:surveyor_id>/surveys/<str:survey_id>/vessel_part/<str:vessel_part_id>/',
        views.surveyor_survey_part_view, name='surveyor-survey-part-view'),
    path('surveyor/<str:surveyor_id>/surveys/<str:survey_id>/vessel_part/<str:vessel_part_id>/sub-part/<str:vessel_subpart_id>/images-preview/',
         views.surveyor_survey_subpart_images_preview_view, name='surveyor-subpart-images-preview'),

    path('surveyor/<str:surveyor_id>/surveys/<str:survey_id>/<str:vessel_part>/<str:vessel_subpart>/view-photo/<str:img_url>',
         views.surveyor_photo_view, name='surveyor-photo-view'),

    path('surveyor/<str:surveyor_id>/surveys/<str:survey_id>/write-survey/<int:page>/',
         views.survey_report_write, name='write-survey'),



]
