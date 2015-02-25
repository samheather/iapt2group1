# Import Auth
from gluon.tools import Auth

# Create BootUp DB if necessary
db = DAL('sqlite://tx.db')

auth = Auth(db)
auth.define_tables(username=True,signature=False)

db.define_table('TranscriptionFieldType',
			Field('type', 'string', requires=IS_LENGTH(minsize=1, maxsize=100), required=True),
			Field('friendlyName', 'string', requires=IS_LENGTH(minsize=1, maxsize=60), required=True)
)

if db(db.TranscriptionFieldType.id > 0).count() == 0:
	db.TranscriptionFieldType.bulk_insert([
						{'type':'textfield','friendlyName':'Text Field'},
						{'type':'textarea','friendlyName':'Multi-lined Text'},
						{'type':'date','friendlyName':'Date Selector'}])
	db.commit()

db.define_table('Project',
			Field('title', 'string', label='Title', requires=IS_LENGTH(minsize=1, maxsize=100), required=True),
			Field('requestDescription', 'string', label='Request Description', requires=IS_LENGTH(minsize=1, maxsize=100), required=True),
			Field('owner_id', db.auth_user, required=True),
			Field('projectOpen', 'boolean', required=True)
)

## TODO - we need to explain our 100 char image description limit below.
db.define_table('Image',
			Field('project_id', db.Project, required=True),
			Field('image', 'upload'),
			Field('imageDescription', 'string', label='Image Description', requires=[IS_LENGTH(minsize=0,error_message="Please enter an image description"),IS_LENGTH(minsize=0, maxsize=100,error_message="Please enter an image description shorter than 100 characters")], required=True)
)

db.define_table('Transcription',
			Field('image_id', db.Image, required=True),
			Field('transcriber_id', db.auth_user, required=True),
			Field('rejected', 'boolean', required=True)
)

"""
Accepted transcription is nullable as the default transcription for a project is none
"""
db.Image.acceptedTranscription_id = Field('acceptedTranscription_id', db.Transcription, required=False)

db.define_table('TranscriptionField',
			Field('projectField_id', db.TranscriptionFieldType, required=True),
			Field('transcription_id', db.Transcription, required=True),
			Field('value', 'string', required=True)
)

db.define_table('ProjectField',
			Field('project_id', db.Project, required=True),
			Field('type_id', db.TranscriptionFieldType, required=True),
			Field('label', 'string', requires=IS_LENGTH(minsize=1, maxsize=20), required=True)
)









# For field type: 'reference TranscriptionFieldType', requires=IS_IN_DB(db, db.TranscriptionFieldType.id, '%(type)s'), required=True), \



