from txform import BOOTSTRAPFORM

# from tx import *

@auth.requires_login()
def summary():
    project_id = request.args(0)  or redirect(URL('default', 'index'))

    if project_id:
        images = db(db.ImagesForTranscription.id == db.Image.id).select(join = db.Image.on(db.Image.project_id == project_id))
    return dict(images=images)

@auth.requires_login()
def image():
    image_id = request.args(0) or redirect(URL('default', 'index'))
    print image_id
    if image_id:
        transcriptions = db(db.Transcription.image_id == image_id).select()
        image = db.Image(image_id)

        fields = []
        for tx in transcriptions:
            fields += db(db.TranscriptionField.transcription_id == tx.id).select()

    return dict(transcriptions=transcriptions
                , fields=fields
                , image=image)