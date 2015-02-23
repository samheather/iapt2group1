# Import Auth
from gluon.tools import Auth

# Create BootUp DB if necessary
db = DAL('sqlite://tx.db')

auth = Auth(db)
auth.define_tables(username=True,signature=False)

db.define_table('TranscriptionFieldType',
			Field('type', 'string', requires=IS_LENGTH(minsize=1, maxsize=100), required=True)
)

if db(db.TranscriptionFieldType.id > 0).count() == 0:
	db.TranscriptionFieldType.bulk_insert([
						{'type':'textfield'},
						{'type':'textarea'},
						{'type':'date'}])
	db.commit()

db.define_table('Project',
			Field('title', 'string', label='Title', requires=IS_LENGTH(minsize=1, maxsize=100), required=True),
			Field('requestDescription', 'string', label='Request Description', requires=IS_LENGTH(minsize=1, maxsize=100), required=True), \
			Field('ownerId', db.auth_user, required=True),
			Field('projectOpen', 'boolean', required=True)
)

## TODO - we need to explain our 100 char image description limit below.
db.define_table('Image',
			Field('projectId', db.Project, required=True),
			Field('image', 'upload'),
			Field('imageDescription', 'string', label='Image Description', requires=[IS_LENGTH(minsize=0,error_message="Please enter an image description"),IS_LENGTH(minsize=0, maxsize=100,error_message="Please enter an image description shorter than 100 characters")], required=True)
)

db.define_table('TranscriptionObject',
			Field('image_id', db.Image, required=True),
			Field('owner_id', db.auth_user, required=True),
			Field('rejected', 'boolean', required=True)
)

"""
Accepted transcription is nullable as the default transcription for a project is none
"""
db.Image.acceptedTranscriptionObject_id = Field('acceptedTranscriptionObject_id', db.TranscriptionObject, required=False)

db.define_table('TranscriptionField',
			Field('type_id', db.TranscriptionFieldType, required=True),
			Field('transcriptionObject_id', db.TranscriptionObject, required=True),
			Field('value', 'string', required=True)
)

db.define_table('FieldsForProject',
			Field('project_id', db.Project, required=True),
			Field('type_id', db.TranscriptionFieldType, required=True),
			Field('label', 'string', requires=IS_LENGTH(minsize=1, maxsize=20), required=True)
)









# For field type: 'reference TranscriptionFieldType', requires=IS_IN_DB(db, db.TranscriptionFieldType.id, '%(type)s'), required=True), \



