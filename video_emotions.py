# from feat import Detector
from .utils import video_emotion_detection
from feat.detector import Detector


def detect_video_emotions(video_path):
    # try:
        vid_name = ''
        if not 'techverx' in video_path:
            vid_name = video_emotion_detection.download_file(video_path)
            video_path = vid_name

        all_ans_emotions = {}

        # loading emotion detector
        # face_model = "retinaface"
        # face_model = "img2pose"
        face_model = "FaceBoxes"
        # face_model = "img2pose"
        landmark_model = "mobilenet"
        au_model = "rf"
        # emotion_model = "resmasknet"
        emotion_model = "fer"
        detector = Detector(face_model=face_model, landmark_model=landmark_model,
                            au_model=au_model, emotion_model=emotion_model)


        emotion_pred = video_emotion_detection.detection(video_path, detector)

        try:
            emotion_indexes = emotion_pred.index.to_list()
            emotion_scores = list(emotion_pred)
            dict_emotions = {}
            for ind, val in enumerate(emotion_indexes):
                dict_emotions[val] = emotion_scores[ind]

            dict_emotions = sorted(dict_emotions.items(),
                                key=lambda x: x[1], reverse=True)
            dict_emotions = dict(dict_emotions)

        except Exception as e:
            print(e)
            dict_emotions = {'Error': "File path is not Given"}

        # if vid_name:
        #     os.remove(vid_name)
        # print('*********************chal raha hai',dict_emotions)
        return dict_emotions
    # except Exception as e:
    #     if vid_name:
    #         os.remove(vid_name)
    #     return {'detections': e}, 400


