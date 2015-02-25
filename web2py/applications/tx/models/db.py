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
			Field('owner_id', db.auth_user, required=True,readable=False,writable=False,default=auth.user_id),
			Field('projectOpen', 'boolean', required=True,readable=False,writable=False,default=False)
)

## TODO - we need to explain our 100 char image description limit below.
db.define_table('Image',
			Field('project_id', db.Project, required=True,readable=False,writable=False),
			Field('image', 'upload'),
			Field('imageDescription', 'string',
                  label='Image Description',
                  requires=[
                      IS_LENGTH(minsize=0,error_message="Please enter an image description"),
                      IS_LENGTH(minsize=0, maxsize=100,error_message="Please enter an image description shorter than 100 characters")],
                  required=True
                  ),
            migrate=False
)


db.executesql('CREATE TABLE IF NOT EXISTS Image '
              '(id              INTEGER PRIMARY KEY AUTOINCREMENT,'
              'project_id        INTEGER REFERENCES Project (id) ON DELETE CASCADE,'
              'image            CHAR(512),'
              'imageDescription CHAR(512),'
              'acceptedTranscription_id INTEGER REFERENCES Image(id) ON DELETE SET NULL)')


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
			Field('project_id', db.Project, required=True,readable=False, writable=False),
			Field('type_id', db.TranscriptionFieldType, required=True),
			Field('label', 'string', requires=IS_LENGTH(minsize=1, maxsize=20), required=True)
)


db.executesql('CREATE VIEW IF NOT EXISTS ImagesForTranscription AS'
              ' SELECT *, COUNT(Transcription.id) AS transcriptionCount'
              ' FROM Image'
              ' LEFT JOIN Transcription ON Transcription.image_id=Image.id'
              ' WHERE Image.acceptedTranscription_id IS NULL'
              '     AND Transcription.rejected IS NOT 1'
              ' GROUP BY Image.id'
              ' HAVING COUNT(Transcription.id)<3')



db.executesql('CREATE VIEW IF NOT EXISTS ProjectsForTranscription AS'
              ' SELECT *, COUNT(ImagesForTranscription.id) AS imageCount'
              ' FROM Project'
              ' LEFT JOIN ImagesForTranscription ON '
              '     ImagesForTranscription.project_id = Project.Id'
              ' WHERE project.projectOpen'
              ' GROUP BY project.id'
              ' HAVING count(ImagesForTranscription.id)>0')



db.define_table('ProjectsForTranscription',
                Field('project_id'),
                Field('image'),
                Field('image_description'),
                Field('imageCount'),migrate=False)



# For field type: 'reference TranscriptionFieldType', requires=IS_IN_DB(db, db.TranscriptionFieldType.id, '%(type)s'), required=True), \


