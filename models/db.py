# Import Auth
from gluon.tools import Auth

# Create BootUp DB if necessary
db = DAL('sqlite://tx.db')

auth = Auth(db)
auth.define_tables(username=True,signature=False)
auth.settings.login_url = URL('user','login')
db.auth_user.password.requires=IS_LENGTH(minsize=6, maxsize=32, error_message="Your password should be between 6 and 32 characters.")
db.auth_user.password.comment="Choose a password between 6 and 32 characters."
db.auth_user.email.comment="Your email should be of the form name@email.com"

db.define_table('TranscriptionFieldType',
			Field('type', 'string', requires=IS_LENGTH(minsize=1, maxsize=100), required=True),
			Field('friendlyName', 'string', requires=IS_LENGTH(minsize=1, maxsize=60), required=True)
)

if db(db.TranscriptionFieldType.id > 0).count() == 0:
	db.TranscriptionFieldType.bulk_insert([
						{'type':'textfield','friendlyName':'Short Text (one line)'},
						{'type':'textarea','friendlyName':'Long Text (multi line)'}])
	db.commit()

db.define_table('Project',
			Field('title', 'string', label='Title', requires=(IS_NOT_EMPTY(error_message="Cannot be empty"), IS_LENGTH(minsize=1, maxsize=100)), required=True),
			Field('requestDescription', 'text', label='Request Description', requires=(IS_NOT_EMPTY(error_message="Cannot be empty"), IS_LENGTH(minsize=1, maxsize=300)), required=True),
			Field('owner_id', db.auth_user, required=True,readable=False,writable=False,default=auth.user_id),
			Field('projectOpen', 'boolean', required=True,readable=False,writable=False,default=False),
            Field.Method('canOpen',lambda row: (row.Project.projectOpen==False)),
            Field.Method('canClose',lambda row: (row.Project.projectOpen)),
)

## TODO - we need to explain our 100 char image description limit below.
db.define_table('Image',
			Field('project_id', db.Project, required=True,readable=False,writable=False),
			Field('image', 'upload'
                   , comment="Maximum file size: 5 MB. Supported image formats: JPG, JPEG, PNG, GIF, BMP."),
			Field('imageDescription', 'string',
                  label='Image Description',
                  requires=[
                      IS_NOT_EMPTY(error_message="Cannot be empty. Please enter an image description shorter than 100 characters"),
                      IS_LENGTH(minsize=1, maxsize=100)],
                  required=True
                  ),
            Field('acceptedTranscription_id', 'reference Transcription', required=False, readable=False, writable=False),
            migrate=False
)

db.Image.image.requires=[IS_NOT_EMPTY(error_message="Please select an image file before proceeding."),
                         IS_IMAGE(error_message="Invalid file. Please select an image in one of these formats: JPG, JPEG, PNG, GIF, BMP."),
                         IS_LENGTH(5242880,0, error_message="Please choose an image which is less than 5 MB.")]

db.define_table('Transcription',
			Field('image_id', db.Image, required=True),
			Field('transcriber_id', db.auth_user, required=True),
			Field('rejected', 'boolean', required=True)
)

db.executesql('CREATE TABLE IF NOT EXISTS Image '
              '(id INTEGER PRIMARY KEY AUTOINCREMENT,'
              'project_id INTEGER REFERENCES Project (id) ON DELETE CASCADE,'
              'image CHAR(512),'
              'imageDescription CHAR(512),'
              'acceptedTranscription_id INTEGER REFERENCES Transcription(id) ON DELETE SET NULL)')


db.define_table('ProjectField',
			Field('project_id', db.Project, required=True,readable=False, writable=False),
			Field('type_id', db.TranscriptionFieldType, required=True, label='Field Type', requires=IS_IN_DB(db,db.TranscriptionFieldType.id,'%(friendlyName)s',zero="Select a field type",error_message="Please select a field type!")),
			Field('label', 'string', requires=[IS_NOT_EMPTY(error_message="Cannot be empty"), IS_LENGTH(minsize=1, maxsize=30)], required=True)
)

db.define_table('TranscriptionField',
			Field('projectField_id', db.ProjectField, required=True),
			Field('transcription_id', db.Transcription, required=True),
			Field('value', 'string', required=True)
)

db.executesql('CREATE VIEW IF NOT EXISTS ImagesForTranscription AS'
              ' SELECT *, COUNT(Transcription.Id) as transcriptionCount FROM Image'
              ' LEFT JOIN Transcription ON (Transcription.Image_Id = Image.id AND (rejected IS NULL or rejected <> "T"))'
              ' WHERE Image.acceptedTranscription_id IS NULL'
              ' GROUP BY Image.Id')

db.executesql('CREATE VIEW IF NOT EXISTS ProjectsForTranscription AS'
              ' SELECT *, COUNT(ImagesForTranscription.id) AS imageCount'
              ' FROM Project'
              ' LEFT JOIN ImagesForTranscription ON '
              '     ImagesForTranscription.project_id = Project.Id'
              ' WHERE project.projectOpen = "T"'
              ' GROUP BY project.id'
              ' HAVING count(ImagesForTranscription.id)>0')

db.executesql('DROP VIEW IF EXISTS ProjectTranscriptionCount')
db.executesql('CREATE VIEW IF NOT EXISTS ProjectTranscriptionCount AS'
              ' SELECT *, COUNT(Transcription.id) AS transcriptionCount, COUNT(Image.id) AS imageCount, COUNT(ProjectField.id) AS fieldCount'
              ' FROM Project'
              ' LEFT JOIN Image ON '
              '     Image.project_id = Project.Id'
              ' LEFT JOIN ProjectField ON '
              '     ProjectField.project_id = Project.Id'
              ' LEFT JOIN Transcription ON'
              '     (Transcription.image_id = Image.id AND (rejected IS NULL or rejected <> "T"))'
              ' GROUP BY project.id')


db.define_table('ImagesForTranscription',
                Field('id'),
                Field('transcriptionCount'),migrate=False)



db.define_table('ProjectsForTranscription',
                Field('id'),
                Field('title'),
                Field('requestDescription'),
                Field('projectOpen'),
                Field('image'),
                Field('imageDescription'),
                Field('imageCount'),migrate=False)
                
db.define_table('ProjectTranscriptionCount',
                Field('id'),
                Field('title'),
                Field('owner_id'),
                Field('image'),
                Field('transcriptionCount'),
                Field('imageCount','integer'),
                Field('fieldCount','integer'),migrate=False)




db.Project.customFields = Field.Method(lambda row: db((db.ProjectField.project_id == row.Project.id) & (db.ProjectField.type_id == db.TranscriptionFieldType.id)).select(db.ProjectField.ALL,db.TranscriptionFieldType.ALL))
db.Project.images = Field.Method(lambda row: db(db.Image.project_id == row.Project.id).select())
db.auth_user.projects = Field.Method(lambda row: db((db.ProjectTranscriptionCount.owner_id == row.auth_user.id) & (db.Project.id == db.ProjectTranscriptionCount.id) &  (db.ProjectTranscriptionCount.fieldCount>0) & (db.ProjectTranscriptionCount.imageCount>0)).select())
db.Image.done = Field.Method(lambda row:
                             True if (len(db(db.ImagesForTranscription.id == row.Image.id )
                                                      .select(db.ImagesForTranscription.transcriptionCount)) == 0)
                                                 or (db(db.ImagesForTranscription.id == row.Image.id )
                                                     .select(db.ImagesForTranscription.transcriptionCount)[0].transcriptionCount>=3)
                             else False)
db.Image.isTranscribedBy = Field.Method(lambda row, transcriber_id:
                                      False if len(db(db.Transcription.image_id == row.Image.id)
                                               .select(db.Transcription.transcriber_id)) ==0
                                      else db(db.Transcription.image_id == row.Image.id)
                                               .select(db.Transcription.transcriber_id)[0].transcriber_id == transcriber_id)
# For field type: 'reference TranscriptionFieldType', requires=IS_IN_DB(db, db.TranscriptionFieldType.id, '%(type)s'), required=True), \
