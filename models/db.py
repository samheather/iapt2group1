# Import Auth
from gluon.tools import Auth

# Create BootUp DB if necessary
db = DAL('sqlite://tx.db')

auth = Auth(db)
auth.define_tables(username=True,signature=False)
auth.settings.login_url = URL('user','login')
db.auth_user.password.requires=IS_LENGTH(minsize=6, error_message="Your password should be longer than 6 characters.")
db.auth_user.password.comment="Enter a password longer than 6 characters."
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
			Field('title', 'string', label='Title', requires=(IS_NOT_EMPTY(error_message="You must enter a title for your project."), IS_LENGTH(minsize=1, maxsize=100, error_message="Your title must be between 1 and 100 characters.")), required=True, comment="Choose a title for your project which is less than 100 characters."),
			Field('requestDescription', 'text', label='Request Description', requires=(IS_NOT_EMPTY(error_message="You must enter a description for your project."), IS_LENGTH(minsize=1, maxsize=300, error_message="Your request description must be between 1 and 300 characters.")), required=True, comment="Choose a request description for your project which is less than 300 characters."),
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
                  comment="Provide a brief description (under 100 characters) for the chosen image.",
                  requires=[
                      IS_NOT_EMPTY(error_message="Please enter an image description, which is shorter than 100 characters"),
                      IS_LENGTH(minsize=1, maxsize=100)],
                  required=True
                  ),
            Field('acceptedTranscription_id', 'reference Transcription', required=False, readable=False, writable=False),
            migrate=False
)

db.Image.image.requires=[IS_NOT_EMPTY(error_message="Please select an image file before proceeding."),
                         IS_IMAGE(error_message="Your file is invalid. Please select an image in one of these formats: JPG, JPEG, PNG, GIF, BMP."),
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
			Field('label', 'string', label='Field Description', requires=[IS_NOT_EMPTY(error_message="You must choose a label for your field e.g. Actor, Title."), IS_LENGTH(minsize=1, maxsize=30)], required=True, comment="Describe what you would like people to transcribe into this Field (e.g. date, document title or author) in under 30 characters.")
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
              ' SELECT Project.*'
              '     , Image.*'
              '     , COUNT(Image.id) as imageCount'
              '     , coalesce(A.transcriptionCount,0) as pendingTranscriptions '
              ' FROM Project '
              '     LEFT JOIN (SELECT '
              '                     Project.id as p_id, '
              '                     COUNT(Transcription.id) transcriptionCount '
              '                FROM Project '
              '                LEFT JOIN Image ON Image.project_id = Project.Id '
              '                LEFT JOIN Transcription ON (Transcription.image_id = Image.id '
              '                                                 and Transcription.rejected is null)'
              '                GROUP BY project.id'
              '                HAVING COUNT(Transcription.id)>0) A'
              '     ON Project.id == A.p_id'
              ' LEFT JOIN Image ON Image.project_id == Project.id '
              ' GROUP BY Project.id')


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
                Field('pendingTranscriptions'),
                Field('imageCount','integer'),migrate=False)



# Get the types of fields, which have been defined for a project.
db.Project.customFields = Field.Method(lambda row: db((db.ProjectField.project_id == row.Project.id) & (db.ProjectField.type_id == db.TranscriptionFieldType.id)).select(db.ProjectField.ALL,db.TranscriptionFieldType.ALL))

# Get all images, which have been added for a project.
db.Project.images = Field.Method(lambda row: db(db.Image.project_id == row.Project.id).select())

# Get total number of fields, which have been added for a project.
db.Project.fieldCount = Field.Method(lambda row: db(row.Project.id == db.ProjectField.project_id).select(db.ProjectField.id.count(), groupby=row.Project.id))

# Get all projects, which have been created by a user.
db.auth_user.projects = Field.Method(lambda row: db((db.ProjectTranscriptionCount.owner_id == row.auth_user.id) & (db.Project.id == db.ProjectTranscriptionCount.id) &  (db.Project.fieldCount>0) & (db.ProjectTranscriptionCount.imageCount>0)).select())

# Check if an image already has three transcriptions, which will close her for the public.
db.Image.done = Field.Method(lambda row:
                             True if (len(db(db.ImagesForTranscription.id == row.Image.id )
                                                      .select(db.ImagesForTranscription.transcriptionCount)) == 0)
                                                 or (db(db.ImagesForTranscription.id == row.Image.id )
                                                     .select(db.ImagesForTranscription.transcriptionCount)[0].transcriptionCount>=3)
                             else False)

# Get all users, who have transcribed an image.
db.Image.transcribedBy = Field.Method(lambda row: db(db.Transcription.image_id == row.Image.id)
                                               .select(db.Transcription.transcriber_id))

# Get total number of transcriptions for a project.
db.Project.total = Field.Method(lambda row: db(db.Project.id == row.Project.id).select(db.Transcription.id.count(), join=[db.Image.on(db.Project.id == db.Image.project_id), db.Transcription.on(db.Transcription.image_id == db.Image.id)]))

# Get total number of transcriptions for an image.
db.Image.total = Field.Method(lambda row: db(row.Image.id == db.Transcription.image_id).select(db.Transcription.id.count()))
