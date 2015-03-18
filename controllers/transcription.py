from txform import BOOTSTRAPFORM

# from tx import *

@auth.requires_login()
def summary():
    project_id = request.args(0)  or redirect(URL('default', 'index'))

    if project_id:
        images = db(db.ImagesForTranscription.id == db.Image.id).select(join = db.Image.on(db.Image.project_id == project_id))
    return dict(images=images)

@auth.requires_login()
def view():
    image_id = request.args(0) or redirect(URL('default', 'index'))
    print image_id
    if image_id:

        # Get all transcriptions for chosen image with the owners
        transcriptions = db(db.Transcription.image_id == image_id).select(left=db.auth_user.on(db.Transcription.transcriber_id == db.auth_user.id))
        image = db.Image(image_id)

        # Get the fields which have been filled out for each transcription and
        # add them to the list. Required are also the field label from the
        # ProjectField table.
        fields = []
        for tx in transcriptions:
            fields += db(db.TranscriptionField.transcription_id == tx.Transcription.id).select(
                left=db.ProjectField.on(
                    db.TranscriptionField.projectField_id==db.ProjectField.id)
                , join=db.TranscriptionFieldType.on(
                    db.TranscriptionFieldType.id==db.ProjectField.type_id))

    return dict(transcriptions=transcriptions
                , fields=fields
                , image=image)