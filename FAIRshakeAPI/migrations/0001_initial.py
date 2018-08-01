# Generated by Django 2.0.7 on 2018-08-01 20:43

from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0009_alter_user_last_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Answer',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('answer', models.TextField(blank=True, default='')),
                ('comment', models.TextField(blank=True, default='')),
                ('url_comment', models.TextField(blank=True, default='')),
            ],
        ),
        migrations.CreateModel(
            name='Assessment',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('methodology', models.TextField(choices=[('self', 'Digital Object Creator Assessment'), ('user', 'Independent User Assessment'), ('auto', 'Automatic Assessment'), ('test', 'Test Assessment')], max_length=16)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='DigitalObject',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('description', models.TextField(blank=True, default='')),
                ('image', models.CharField(blank=True, default='', max_length=255)),
                ('tags', models.CharField(blank=True, default='', max_length=255)),
                ('type', models.CharField(blank=True, choices=[('', 'Other'), ('any', 'Any Digital Object'), ('data', 'Dataset'), ('repo', 'Repository'), ('test', 'Test Object'), ('tool', 'Tool')], default='', max_length=16)),
                ('title', models.CharField(blank=True, default='', max_length=255)),
                ('url', models.CharField(max_length=255)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Metric',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=255)),
                ('url', models.CharField(blank=True, default='', max_length=255)),
                ('description', models.TextField(blank=True, default='')),
                ('image', models.CharField(blank=True, default='', max_length=255)),
                ('tags', models.CharField(blank=True, default='', max_length=255)),
                ('type', models.CharField(blank=True, choices=[('yesnobut', 'Yes no or but question'), ('text', 'Simple textbox input'), ('url', 'A url input')], default='yesnobut', max_length=16)),
                ('license', models.CharField(blank=True, default='', max_length=255)),
                ('rationale', models.TextField(blank=True, default='')),
                ('principle', models.CharField(blank=True, choices=[('F', 'Findability'), ('A', 'Accessibility'), ('I', 'Interoperability'), ('R', 'Reusability')], default='', max_length=16)),
                ('fairmetrics', models.CharField(blank=True, default='', max_length=255)),
                ('fairsharing', models.CharField(blank=True, default='', max_length=255)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=255)),
                ('url', models.CharField(blank=True, default='', max_length=255)),
                ('description', models.TextField(blank=True, default='')),
                ('image', models.CharField(blank=True, default='', max_length=255)),
                ('tags', models.CharField(blank=True, default='', max_length=255)),
                ('type', models.CharField(blank=True, choices=[('', 'Other'), ('any', 'Any Digital Object'), ('data', 'Dataset'), ('repo', 'Repository'), ('test', 'Test Object'), ('tool', 'Tool')], default='', max_length=16)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Rubric',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=255)),
                ('url', models.CharField(blank=True, default='', max_length=255)),
                ('description', models.TextField(blank=True, default='')),
                ('image', models.CharField(blank=True, default='', max_length=255)),
                ('tags', models.CharField(blank=True, default='', max_length=255)),
                ('type', models.CharField(blank=True, choices=[('', 'Other'), ('any', 'Any Digital Object'), ('data', 'Dataset'), ('repo', 'Repository'), ('test', 'Test Object'), ('tool', 'Tool')], default='', max_length=16)),
                ('license', models.CharField(blank=True, default='', max_length=255)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Author',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.AddField(
            model_name='rubric',
            name='authors',
            field=models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='rubric',
            name='metrics',
            field=models.ManyToManyField(blank=True, related_name='rubrics', to='FAIRshakeAPI.Metric'),
        ),
        migrations.AddField(
            model_name='project',
            name='authors',
            field=models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='project',
            name='digital_objects',
            field=models.ManyToManyField(blank=True, related_name='projects', to='FAIRshakeAPI.DigitalObject'),
        ),
        migrations.AddField(
            model_name='metric',
            name='authors',
            field=models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='digitalobject',
            name='authors',
            field=models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='digitalobject',
            name='rubrics',
            field=models.ManyToManyField(blank=True, related_name='digital_objects', to='FAIRshakeAPI.Rubric'),
        ),
        migrations.AddField(
            model_name='assessment',
            name='assessor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='assessment',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='assessments', to='FAIRshakeAPI.Project'),
        ),
        migrations.AddField(
            model_name='assessment',
            name='requestor',
            field=models.ForeignKey(blank=True, default='', on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='assessment',
            name='rubric',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='assessments', to='FAIRshakeAPI.Rubric'),
        ),
        migrations.AddField(
            model_name='assessment',
            name='target',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='assessments', to='FAIRshakeAPI.DigitalObject'),
        ),
        migrations.AddField(
            model_name='answer',
            name='assessment',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='answers', to='FAIRshakeAPI.Assessment'),
        ),
        migrations.AddField(
            model_name='answer',
            name='metric',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='answers', to='FAIRshakeAPI.Metric'),
        ),
    ]
