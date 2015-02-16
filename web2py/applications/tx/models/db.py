# Import Auth
from gluon.tools import Auth

# Create BootUp DB if necessary
db = DAL('sqlite://bootup.db')

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
			Field('title', 'string', label='Title', requires=IS_LENGTH(minsize=1, maxsize=100), required=True), \
			Field('requestDescription', 'string', label='Request Description', requires=IS_LENGTH(minsize=1, maxsize=100), required=True), \
			Field('ownerId', db.auth_user, required=True), \
			Field('projectOpen', 'boolean', required=True)
)

db.define_table('TranscriptionObject',
#			Field('image_id', db.Image, required=True), \
			Field('owner_id', db.auth_user, required=True), \
			Field('rejected', 'boolean', required=True)
)

## TODO - we need to explain our 100 char image description limit below.
db.define_table('Image',
			Field('projectId', db.Project, required=True), \
			Field('image', 'upload'), \
			Field('imageDescription', 'string', label='Image Description', requires=IS_LENGTH(minsize=1, maxsize=100), required=True), \
			Field('acceptedTranscriptionObject_id', db.TranscriptionObject)
)

db.TranscriptionObject.image_id = Field('image_id', db.Image, required=True)




# For field type: 'reference TranscriptionFieldType', requires=IS_IN_DB(db, db.TranscriptionFieldType.id, '%(type)s'), required=True), \