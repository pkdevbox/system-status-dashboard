#
# Copyright 2013 - Tom Alessi
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


"""Form and Form Field classes for the SSD project

   All fields should be defined first, with forms to follow.  Form fields
   have basic validation rules and DJango takes care of escaping anything
   dangerous automatically.

"""

import os
import datetime
import re
from django import forms
from django.conf import settings
from ssd.main.models import Config
from ssd.main.models import Config_Email
from ssd.main.models import Config_Ireport



### VALIDATORS ###

def file_size(value):
    """Ensure file size is below the maximum allowed"""

    # Obtain the max file size
    file_size = Config_Ireport.objects.filter(id=Config_Ireport.objects.values('id')[0]['id']).values('file_size')[0]['file_size']

    if value.size > file_size:
        raise forms.ValidationError('File too large (%s bytes) - please reduce the size of the upload to below %s bytes.' % (value.size,file_size))


### FIELDS ###


class MultipleServiceField(forms.Field):
    """Multiple service checkbox/input field

       Requirements:
          - Must not be empty (at least one service must be provided)

    """

    def validate(self, value):
        if value is None or value == '':
            raise forms.ValidationError('Select at least one item.')


### FORMS ###


class EmailConfigForm(forms.Form):
    """Form for modifying the admin email configuration

        Email Format:
            - 0 = text
            - 1 = html
    """

    enabled = forms.BooleanField(required=False)
    email_format = forms.BooleanField(required=False)
    from_address = forms.EmailField(required=False)
    text_pager = forms.EmailField(required=False)
    incident_greeting = forms.CharField(required=False)
    incident_update = forms.CharField(required=False)
    maintenance_greeting = forms.CharField(required=False)
    maintenance_update = forms.CharField(required=False)

    # Override the form clean method - there is some special logic to validate 

    def clean(self):
        cleaned_data = super(EmailConfigForm, self).clean()
        enabled = cleaned_data.get('enabled')
        from_address = cleaned_data.get('from_address')
        text_pager = cleaned_data.get('text_pager')
        incident_greeting = cleaned_data.get('incident_greeting')
        incident_update = cleaned_data.get('incident_update')
        maintenance_greeting = cleaned_data.get('maintenance_greeting')
        maintenance_update = cleaned_data.get('maintenance_update')


        # Cannot enabled email functionality without defining all values
        if enabled and not from_address:
            # Make sure its an integer
            self._errors["enabled"] = self.error_class(['Cannot enable email functionality without defining all options.'])
            self._errors["from_address"] = self.error_class(['This field is required.'])

        if enabled and not incident_greeting:
            # Make sure its an integer
            self._errors["enabled"] = self.error_class(['Cannot enable email functionality without defining all options.'])
            self._errors["incident_greeting"] = self.error_class(['This field is required.'])

        if enabled and not incident_update:
            # Make sure its an integer
            self._errors["enabled"] = self.error_class(['Cannot enable email functionality without defining all options.'])
            self._errors["incident_update"] = self.error_class(['This field is required.'])

        if enabled and not maintenance_greeting:
            # Make sure its an integer
            self._errors["enabled"] = self.error_class(['Cannot enable email functionality without defining all options.'])
            self._errors["maintenance_greeting"] = self.error_class(['This field is required.'])

        if enabled and not maintenance_update:
            # Make sure its an integer
            self._errors["enabled"] = self.error_class(['Cannot enable email functionality without defining all options.'])
            self._errors["maintenance_update"] = self.error_class(['This field is required.'])


        # If incident reports are enabled, and email notifications for incident reports are enabled, then a text pager 
        # recipient must be defined
        ireport_config = Config_Ireport.objects.filter(id=Config_Ireport.objects.values('id')[0]['id']).values('enabled','email_enabled')
        # If email is being enabled without a text pager address and incident reports with email are turned on, error
        if enabled and not text_pager and ireport_config[0]['enabled'] == 1 and ireport_config[0]['email_enabled'] == 1:
            self._errors["text_pager"] = self.error_class(['A text pager email address must be provided if incident reports with email notifications are enabled'])
        # If email is being disabled, see if incident reports and associated emails are enabled
        if not enabled:
            if ireport_config[0]['enabled'] == 1 and ireport_config[0]['email_enabled'] == 1:
                # Yes they are, so cannot disable email notification
                self._errors["enabled"] = self.error_class(['Cannot disable email functionality if incident reports with email notifications are enabled.'])


        # Return the full collection of cleaned data
        return cleaned_data

class MessagesConfigForm(forms.Form):
    """Form for modifying the admin messages configuration"""

    main = forms.CharField(required=False)
    main_enabled = forms.BooleanField(required=False)
    alert = forms.CharField(required=False)
    alert_enabled = forms.BooleanField(required=False)


    # Override the form clean method - there is some special logic to validate 
    def clean(self):
        cleaned_data = super(MessagesConfigForm, self).clean()
        main = cleaned_data.get('main')
        main_enabled = cleaned_data.get('main_enabled')
        alert = cleaned_data.get('alert')
        alert_enabled = cleaned_data.get('alert_enabled')


        # Cannot enabled messages if there is no text
        if main_enabled and not main:
            # Make sure its an integer
            self._errors["main"] = self.error_class(['Please enter a system message'])
            self._errors["main_enabled"] = self.error_class(['Cannot enable the system message without defining one'])

        if alert_enabled and not alert:
            # Make sure its an integer
            self._errors["alert"] = self.error_class(['Please enter a system alert'])
            self._errors["alert_enabled"] = self.error_class(['Cannot enable the system alert without defining one'])
     
        # Return the full collection of cleaned data
        return cleaned_data


class LogoConfigForm(forms.Form):
    """Form for modifying the admin logo configuration"""

    url = forms.CharField(required=False)
    logo_enabled = forms.BooleanField(required=False)


    # Override the form clean method - there is some special logic to validate 
    def clean(self):
        cleaned_data = super(LogoConfigForm, self).clean()
        url = cleaned_data.get('url')
        logo_enabled = cleaned_data.get('logo_enabled')

        # Cannot enabled the logo if there is no url
        if logo_enabled and not url:
            # Make sure its an integer
            self._errors["url"] = self.error_class(['Please enter a logo url'])
            self._errors["logo_enabled"] = self.error_class(['Cannot enable the logo without a logo defined'])
     
        # Return the full collection of cleaned data
        return cleaned_data


class SystemurlConfigForm(forms.Form):
    """Form for modifying the admin system url configuration"""

    url = forms.URLField(required=False)
    url_enabled = forms.BooleanField(required=False)


    # Override the form clean method - there is some special logic to validate 
    def clean(self):
        cleaned_data = super(SystemurlConfigForm, self).clean()
        url = cleaned_data.get('url')
        url_enabled = cleaned_data.get('url_enabled')

        # Cannot enabled the logo if there is no url
        if url_enabled and not url:
            # Make sure its an integer
            self._errors["url"] = self.error_class(['Please enter a system url'])
            self._errors["url_enabled"] = self.error_class(['Cannot enable the system url without a url defined'])
     
        # Return the full collection of cleaned data
        return cleaned_data


class IreportConfigForm(forms.Form):
    """Form for modifying the admin incident report configuration"""

    enabled = forms.BooleanField(required=False)
    email_enabled = forms.BooleanField(required=False)
    instructions = forms.CharField(required=True)
    submit_message = forms.CharField(required=True)
    upload_path = forms.CharField(required=False)
    upload_enabled = forms.BooleanField(required=False)
    file_size = forms.IntegerField(required=False)


    # Override the form clean method - there is some special logic to validate 
    def clean(self):
        cleaned_data = super(IreportConfigForm, self).clean()
        email_enabled = cleaned_data.get('email_enabled')
        upload_path = cleaned_data.get('upload_path')
        upload_enabled = cleaned_data.get('upload_enabled')
        file_size = cleaned_data.get('file_size')

        # Cannot enable uploads w/o an upload path
        if upload_enabled and not upload_path:
            self._errors["upload_path"] = self.error_class(['Please enter a local upload path.'])
            self._errors["upload_enabled"] = self.error_class(['Cannot enable file uploads without defining an upload path.'])
     
        # File size needs to be larger than 0
        if file_size == 0:
            self._errors["file_size"] = self.error_class(['Please enter a file size of at least 1.'])

        if file_size and file_size < 0:
            # Make sure its a positive integer
            self._errors["file_size"] = self.error_class(['Please enter a positive integer.'])

        # If the upload path is defined and does not exist or is not writable, that's an error
        if upload_path:
            # Writable?
            if not os.access(upload_path, os.W_OK):
                self._errors["upload_path"] = self.error_class(['This location is not writable by the Apache user.'])

            # Exists?
            if not os.path.exists(upload_path):
                self._errors["upload_path"] = self.error_class(['This location does not exist.'])

        # Email notifications cannot be enabled if global email is disabled
        global_email_config = Config_Email.objects.filter(id=Config_Email.objects.values('id')[0]['id']).values('enabled','text_pager')
        if email_enabled:
            if not global_email_config[0]['enabled']:
                self._errors["email_enabled"] = self.error_class(['Global email must be enabled to enable this option.'])
            if not global_email_config[0]['text_pager'] :
                self._errors["email_enabled"] = self.error_class(['A text pager recipient must be defined within the global email options in order to enable this option.'])

        # Return the full collection of cleaned data
        return cleaned_data


class EscalationConfigForm(forms.Form):
    """Form for modifying the admin escalation configuration"""

    enabled = forms.BooleanField(required=False)


class DetailForm(forms.Form):
    """Form for obtaining the detail about an existing event (incident or maintenance)"""

    id = forms.IntegerField()


class DeleteEventForm(forms.Form):
    """Form for deleting an existing event (incident or maintenance)"""

    id = forms.IntegerField()


class UpdateTZForm(forms.Form):
    """Form for setting or updating the timezone"""

    timezone = forms.CharField(required=True)


class JumpToForm(forms.Form):
    """Form for setting the calendar view date"""

    jump_to = forms.DateField(required=True,input_formats=['%Y-%m-%d'])


class ReportIncidentForm(forms.Form):
    """Form for reporting an incident (by a user)"""

    name = forms.CharField(required=True)
    email = forms.EmailField(required=True)
    detail = forms.CharField(required=True)
    extra = forms.CharField(required=False)
    screenshot1 = forms.ImageField(required=False,validators=[file_size])
    screenshot2 = forms.ImageField(required=False,validators=[file_size])


class SearchForm(forms.Form):
    """Form for searching through events

    """

    s_date = forms.DateField(required=True,input_formats=['%Y-%m-%d'])
    s_time = forms.TimeField(required=True,input_formats=['%H:%M'])
    e_date = forms.DateField(required=True,input_formats=['%Y-%m-%d'])
    e_time = forms.TimeField(required=True,input_formats=['%H:%M'])
    status = forms.CharField(required=False)
    text = forms.CharField(required=False)


class IGSearchForm(forms.Form):
    """Form for searching through incidents from the summary graph

    """

    date = forms.DateField(required=True,input_formats=['%Y-%m-%d'])


class MSearchForm(forms.Form):
    """Form for searching through scheduled maintenance

    """

    s_date = forms.DateField(required=True,input_formats=['%Y-%m-%d'])
    s_time = forms.TimeField(required=True,input_formats=['%H:%M'])
    e_date = forms.DateField(required=True,input_formats=['%Y-%m-%d'])
    e_time = forms.TimeField(required=True,input_formats=['%H:%M'])
    text = forms.CharField(required=False)


class AddEmailForm(forms.Form):
    """Form for adding email recipients"""

    email = forms.EmailField(required=True)


class IncidentReportListForm(forms.Form):
    """Form for querying incident reports"""

    page = forms.IntegerField(required=False)


class RemoveEmailForm(forms.Form):
    """Form for removing remail recipients"""

    id = MultipleServiceField()


class AddContactForm(forms.Form):
    """Form for adding escalation contacts"""

    name = forms.CharField(required=True)
    contact_details = forms.CharField(required=True)


class AddServiceForm(forms.Form):
    """Form for adding services"""

    service = forms.CharField(required=True)


class RemoveServiceForm(forms.Form):
    """Form for removing services"""

    id = MultipleServiceField()


class ModifyContactForm(forms.Form):
    """Form for removing contacts"""

    id = forms.IntegerField(required=True)
    action = forms.CharField(required=True)


class ConfigAdminForm(forms.ModelForm):
    """DJango form for creating a larger textarea to make it easier
       to create/edit the configs

    """

    config_value = forms.CharField(widget=forms.Textarea)
    class Meta:
        model = Config


class ConfigForm(forms.Form):
    """Form for updating configs"""

    recipient_name = forms.CharField(required=False)
    greeting_incident_new = forms.CharField(required=False)
    greeting_incident_update = forms.CharField(required=False)
    email_format_maintenance = forms.IntegerField(required=False)
    email_format_incident = forms.IntegerField(required=False)
    email_from = forms.EmailField(required=False)
    email_subject_incident = forms.CharField(required=False)
    email_subject_maintenance = forms.CharField(required=False)
    greeting_maintenance_new = forms.CharField(required=False)
    greeting_maintenance_update = forms.CharField(required=False)
    recipient_pager = forms.EmailField(required=False)
    message_success = forms.CharField(required=False)
    message_error = forms.CharField(required=False)
    notify = forms.IntegerField(required=False)
    instr_incident_description = forms.CharField(required=False)
    instr_incident_update = forms.CharField(required=False)
    instr_maintenance_impact = forms.CharField(required=False)
    instr_maintenance_coordinator = forms.CharField(required=False)
    instr_maintenance_update = forms.CharField(required=False)
    instr_maintenance_description = forms.CharField(required=False)    
    instr_report_name = forms.CharField(required=False)
    instr_report_email = forms.CharField(required=False)
    instr_report_detail = forms.CharField(required=False)
    instr_report_extra = forms.CharField(required=False)
    instr_escalation_name = forms.CharField(required=False)
    instr_escalation_details = forms.CharField(required=False)
    logo_display = forms.IntegerField(required=False)
    logo_url = forms.CharField(required=False)
    nav_display = forms.IntegerField(required=False)
    escalation_display = forms.IntegerField(required=False)
    report_incident_display = forms.IntegerField(required=False)
    login_display = forms.IntegerField(required=False)
    display_alert = forms.CharField(required=False)
    alert = forms.CharField(required=False)
    help_sched_maint = forms.CharField(required=False)
    help_report_incident = forms.CharField(required=False)
    help_create_incident = forms.CharField(required=False)
    help_escalation = forms.CharField(required=False)    
    enable_uploads = forms.IntegerField(required=False)
    upload_path = forms.CharField(required=False)
    enable_uploads = forms.IntegerField(required=False)
    upload_path = forms.CharField(required=False)
    file_upload_size = forms.CharField(required=False)
    ssd_url = forms.CharField(required=False)
    escalation = forms.CharField(required=False)
    information_main = forms.CharField(required=False)    

    filter = forms.CharField(required=False)

    # We need access to some of the update_ values, but only some.
    update_enable_uploads = forms.BooleanField(required=False)
    update_file_upload_size = forms.BooleanField(required=False)
    update_upload_path = forms.BooleanField(required=False)

    # Override the form clean method - there is some special logic to validate 

    def clean(self):
        cleaned_data = super(ConfigForm, self).clean()
        enable_uploads = cleaned_data.get('enable_uploads')
        update_enable_uploads = cleaned_data.get('update_enable_uploads')
        upload_path = cleaned_data.get('upload_path')
        update_upload_path = cleaned_data.get('update_upload_path')
        file_upload_size = cleaned_data.get('file_upload_size')
        update_file_upload_size = cleaned_data.get('update_file_upload_size')

        # File uploads must be an integer, not be blank, and be at least 100
        # This is only relevant when the value is being updated (its set at install time at 1024)
        if update_file_upload_size:
            # Make sure its an integer
            if re.match(r'^\d+$', file_upload_size):
                if int(file_upload_size) < 100:
                    self._errors["file_upload_size"] = self.error_class(['File size must be at least 100.'])
            else:
                self._errors["file_upload_size"] = self.error_class(['Please enter a whole number.'])    
     
        # If we are enabling uploads (as in they are not enabled), then make sure the upload path is set
        if update_enable_uploads and enable_uploads and not upload_path:
            # A new upload path is not being set but maybe its already set in the DB
            d_upload_path = Config.objects.filter(config_name='upload_path').values('config_value')[0]['config_value']
            if not d_upload_path:
                self._errors["upload_path"] = self.error_class(['You must set a file upload path if uploads are enabled.'])

        # If we are removing the upload path, make sure file uploads are not enabled
        if update_upload_path and not enable_uploads and not upload_path:
            # We are not enabling uploads at the same time, maybe its already set in the DB
            d_enable_uploads = int(Config.objects.filter(config_name='enable_uploads').values('config_value')[0]['config_value'])
            if d_enable_uploads:
                self._errors["upload_path"] = self.error_class(['You must set a file upload path if uploads are enabled.'])


        # Return the full collection of cleaned data
        return cleaned_data


class AddIncidentForm(forms.Form):
    """Form for adding a new incident (by an administrator)"""

    s_date = forms.DateField(required=True,input_formats=['%Y-%m-%d'])
    s_time = forms.TimeField(required=True,input_formats=['%H:%M'])
    e_date = forms.DateField(required=False,input_formats=['%Y-%m-%d'])
    e_time = forms.TimeField(required=False,input_formats=['%H:%M'])
    detail = forms.CharField(required=True)
    service = MultipleServiceField()
    broadcast = forms.BooleanField(required=False)
    email_id = forms.IntegerField(required=False)

    # Override the form clean method - there is some special logic to 
    # adding an incident and we need access to multiple values
    # to do it.

    def clean(self):
        cleaned_data = super(AddIncidentForm, self).clean()
        s_date = cleaned_data.get('s_date')
        s_time = cleaned_data.get('s_time')
        e_date = cleaned_data.get('e_date')
        e_time = cleaned_data.get('e_time')
        broadcast = cleaned_data.get('broadcast')
        email_id = cleaned_data.get('email_id')

        # If an email broadcast is requested, an email address must accompany it
        if broadcast and not email_id:
            self._errors["broadcast"] = self.error_class(['Cannot broadcast if no address selected.'])

        # If there is an end date but not an end time (or vice versa, error)
        if e_date and not e_time:
            self._errors["e_time"] = self.error_class(['You must provide an end time'])
        
        if e_time and not e_date:
            self._errors["e_date"] = self.error_class(['You must provide an end date'])

        # If there is a start and end date/time, then ensure they are in the proper order
        if s_date and s_time and e_date and e_time:

            # Ensure the end date/time is not before the start date/time
            start,end = None,None
            try:
                # Combine the dates and times into datetime objects (improperly formated dates/times will cause exceptions)
                start = datetime.datetime.combine(s_date, s_time)
            except Exception:
                self._errors["s_date"] = self.error_class(['Empty or improperly formatted date or time'])
                self._errors["s_time"] = self.error_class(['Empty or improperly formatted date or time'])

            try:
                # Combine the dates and times into datetime objects (improperly formated dates/times will cause exceptions)
                end = datetime.datetime.combine(e_date, e_time)
            except Exception:
                self._errors["e_date"] = self.error_class(['Empty or improperly formatted date or time'])
                self._errors["e_time"] = self.error_class(['Empty or improperly formatted date or time'])
                
            if start and end:
                if start > end:
                    self._errors["s_date"] = self.error_class(['End date/time must be after start date/time'])
                    self._errors["s_time"] = self.error_class(['End date/time must be after start date/time'])
                    self._errors["e_date"] = self.error_class(['End date/time must be after start date/time'])
                    self._errors["e_time"] = self.error_class(['End date/time must be after start date/time'])         
        
        # Return the full collection of cleaned data
        return cleaned_data


class UpdateIncidentForm(forms.Form):
    """Form for updating an existing incident"""

    id = forms.IntegerField()
    s_date = forms.DateField(required=True,input_formats=['%Y-%m-%d'])
    s_time = forms.TimeField(required=True,input_formats=['%H:%M'])
    e_date = forms.DateField(required=False,input_formats=['%Y-%m-%d'])
    e_time = forms.TimeField(required=False,input_formats=['%H:%M'])
    detail = forms.CharField(required=True)
    update = forms.CharField(required=False)
    service = MultipleServiceField()
    broadcast = forms.BooleanField(required=False)
    email_id = forms.IntegerField(required=False)

    # Override the form clean method - there is some special logic to 
    # creating an incident and we need access to multiple values
    # to do it.

    def clean(self):
        cleaned_data = super(UpdateIncidentForm, self).clean()
        s_date = cleaned_data.get('s_date')
        s_time = cleaned_data.get('s_time')
        e_date = cleaned_data.get('e_date')
        e_time = cleaned_data.get('e_time')
        broadcast = cleaned_data.get('broadcast')
        email_id = cleaned_data.get('email_id')

        # If an email broadcast is requested, an email address must accompany it
        if broadcast and not email_id:
            self._errors["broadcast"] = self.error_class(['Cannot broadcast if no email address selected.'])

        # If there is an end date but not an end time (or vice versa, error)
        if e_date and not e_time:
            self._errors["e_time"] = self.error_class(['You must provide an end time'])
        
        if e_time and not e_date:
            self._errors["e_date"] = self.error_class(['You must provide an end date'])

        # If there is a start and end date/time, then ensure they are in the proper order
        if s_date and s_time and e_date and e_time:

            # Ensure the end date/time is not before the start date/time
            start,end = None,None
            try:
                # Combine the dates and times into datetime objects (improperly formated dates/times will cause exceptions)
                start = datetime.datetime.combine(s_date, s_time)
            except Exception:
                self._errors["s_date"] = self.error_class(['Empty or improperly formatted date or time'])
                self._errors["s_time"] = self.error_class(['Empty or improperly formatted date or time'])

            try:
                # Combine the dates and times into datetime objects (improperly formated dates/times will cause exceptions)
                end = datetime.datetime.combine(e_date, e_time)
            except Exception:
                self._errors["e_date"] = self.error_class(['Empty or improperly formatted date or time'])
                self._errors["e_time"] = self.error_class(['Empty or improperly formatted date or time'])
                
            if start and end:
                if start > end:
                    self._errors["s_date"] = self.error_class(['End date/time must be after start date/time'])
                    self._errors["s_time"] = self.error_class(['End date/time must be after start date/time'])
                    self._errors["e_date"] = self.error_class(['End date/time must be after start date/time'])
                    self._errors["e_time"] = self.error_class(['End date/time must be after start date/time'])    
                    
        # Return the full collection of cleaned data
        return cleaned_data


class EmailMaintenanceForm(forms.Form):
    """Form for emailing about maintenance"""

    id = forms.IntegerField(required=True)


class AddMaintenanceForm(forms.Form):
    """Form for adding maintenance"""

    s_date = forms.DateField(required=True,input_formats=['%Y-%m-%d'])
    s_time = forms.TimeField(required=True,input_formats=['%H:%M'])
    e_date = forms.DateField(required=True,input_formats=['%Y-%m-%d'])
    e_time = forms.TimeField(required=True,input_formats=['%H:%M'])
    description = forms.CharField(required=True)
    impact = forms.CharField(required=False)
    coordinator = forms.CharField(required=False)
    service = MultipleServiceField()
    broadcast = forms.BooleanField(required=False)
    email_id = forms.IntegerField(required=False)

    # Override the form clean method - there is some special logic to 
    # scheduling a maintenance and we need access to multiple values
    # to do it.

    def clean(self):
        cleaned_data = super(AddMaintenanceForm, self).clean()
        broadcast = cleaned_data.get('broadcast')
        email_id = cleaned_data.get('email_id')
        s_date = cleaned_data.get('s_date')
        s_time = cleaned_data.get('s_time')
        e_date = cleaned_data.get('e_date')
        e_time = cleaned_data.get('e_time')


        # If email broadcast is selected, an email address also must be
        if broadcast and not email_id:
            self._errors["broadcast"] = self.error_class(['Cannot broadcast if no address selected.'])
        
        # Ensure the end date/time is not before the start date/time
        start,end = None,None
        try:
            # Combine the dates and times into datetime objects (improperly formated dates/times will cause exceptions)
            start = datetime.datetime.combine(s_date, s_time)
        except Exception:
            self._errors["s_date"] = self.error_class(['Empty or improperly formatted date or time'])
            self._errors["s_time"] = self.error_class(['Empty or improperly formatted date or time'])

        try:
            # Combine the dates and times into datetime objects (improperly formated dates/times will cause exceptions)
            end = datetime.datetime.combine(e_date, e_time)
        except Exception:
            self._errors["e_date"] = self.error_class(['Empty or improperly formatted date or time'])
            self._errors["e_time"] = self.error_class(['Empty or improperly formatted date or time'])
            
        if start and end:
            if start > end:
                self._errors["s_date"] = self.error_class(['End date/time must be after start date/time'])
                self._errors["e_date"] = self.error_class(['End date/time must be after start date/time'])
        
        # Return the full collection of cleaned data
        return cleaned_data


class UpdateMaintenanceForm(forms.Form):
    """Form for updating maintenance"""

    s_date = forms.DateField(required=True,input_formats=['%Y-%m-%d'])
    s_time = forms.TimeField(required=True,input_formats=['%H:%M'])
    e_date = forms.DateField(required=True,input_formats=['%Y-%m-%d'])
    e_time = forms.TimeField(required=True,input_formats=['%H:%M'])
    description = forms.CharField(required=True)
    impact = forms.CharField(required=False)
    coordinator = forms.CharField(required=False)
    update = forms.CharField(required=False)
    service = MultipleServiceField()
    id = forms.IntegerField(required=True)
    started = forms.CharField(required=False)
    completed = forms.CharField(required=False)
    broadcast = forms.BooleanField(required=False)
    email_id = forms.IntegerField(required=False)
    

    # Override the form clean method - to validate the special logic in this form
    def clean(self):
        cleaned_data = super(UpdateMaintenanceForm, self).clean()
        s_date = cleaned_data.get('s_date')
        s_time = cleaned_data.get('s_time')
        e_date = cleaned_data.get('e_date')
        e_time = cleaned_data.get('e_time')
        broadcast = cleaned_data.get("broadcast")
        email_id = cleaned_data.get("email_id")
        started = cleaned_data.get('started')
        completed = cleaned_data.get('completed')

        # If an email broadcast is requested but no email address is selected, error
        if broadcast and not email_id:
            # Set custom error messages
            self._errors["broadcast"] = self.error_class(['Cannot broadcast if no address selected.'])
        
        # If its completed, make sure its started
        if completed and not started:
            # Set custom error messages
            self._errors['completed'] = self.error_class(['Maintenance cannot be completed if not started.'])

        # Ensure the end date/time is not before the start date/time
        
        start,end = None,None
        try:
            # Combine the dates and times into datetime objects (improperly formated dates/times will cause exceptions)
            start = datetime.datetime.combine(s_date, s_time)
        except Exception:
            self._errors["s_date"] = self.error_class(['Empty or improperly formatted date or time'])
            self._errors["s_time"] = self.error_class(['Empty or improperly formatted date or time'])

        try:
            # Combine the dates and times into datetime objects (improperly formated dates/times will cause exceptions)
            end = datetime.datetime.combine(e_date, e_time)
        except Exception:
            self._errors["e_date"] = self.error_class(['Empty or improperly formatted date or time'])
            self._errors["e_time"] = self.error_class(['Empty or improperly formatted date or time'])
            
        if start and end:
            if start > end:
                self._errors["s_date"] = self.error_class(['End date/time must be after start date/time'])
                self._errors["e_date"] = self.error_class(['End date/time must be after start date/time'])

        # Return the full collection of cleaned data
        return cleaned_data