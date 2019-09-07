from zipfile import ZipFile
import pandas as pd
import cv2
import gc
import os
import numpy as np
from tqdm import tqdm
import matplotlib.pyplot as plt
from Utils.postprocessing import make_submission

fns = [

    '/media/hdd/Kaggle/Pneumothorax/Data/Preds/PANetDilatedResNet34_768_Fold0/pred_tta.zip',
    '/media/hdd/Kaggle/Pneumothorax/Data/Preds/PANetDilatedResNet34_768_Fold1/pred_tta.zip',
    '/media/hdd/Kaggle/Pneumothorax/Data/Preds/PANetDilatedResNet34_768_Fold3/pred_tta.zip',
    '/media/hdd/Kaggle/Pneumothorax/Data/Preds/PANetDilatedResNet34_768_Fold4/pred_tta.zip',

    '/media/hdd/Kaggle/Pneumothorax/Data/Preds/PANetResNet50_768_Fold0/pred_tta.zip',
    '/media/hdd/Kaggle/Pneumothorax/Data/Preds/PANetResNet50_768_Fold1/pred_tta.zip',
    '/media/hdd/Kaggle/Pneumothorax/Data/Preds/PANetResNet50_768_Fold2/pred_tta.zip',
    '/media/hdd/Kaggle/Pneumothorax/Data/Preds/PANetResNet50_768_Fold3/pred_tta.zip',

    '/media/hdd/Kaggle/Pneumothorax/Data/Preds/EMANetResNet101_768_Fold7/pred_tta.zip',
    '/media/hdd/Kaggle/Pneumothorax/Data/Preds/EMANetResNet101_768_Fold8/pred_tta.zip',

    'Model_000_f00/f00-PREDS.zip',
    'Model_000_f01/f01-PREDS.zip',
    'Model_000_f02/f02-PREDS.zip',
    'Model_000_f03/f03-PREDS.zip',
    'Model_000_f04/f04-PREDS.zip',

    'Model_001_f00/f00-PREDS.zip',
    'Model_001_f01/f01-PREDS.zip',
    'Model_001_f02/f02-PREDS.zip',
    'Model_001_f03/f03-PREDS.zip',
    'Model_001_f04/f04-PREDS.zip',

    '/media/hdd/Kaggle/Pneumothorax/Data/Preds/PANetDilatedResNet34_768_Fold5_ptx/pred_tta.zip',
    '/media/hdd/Kaggle/Pneumothorax/Data/Preds/PANetDilatedResNet34_768_Fold6_ptx/pred_tta.zip',
    '/media/hdd/Kaggle/Pneumothorax/Data/Preds/PANetDilatedResNet34_768_Fold7_ptx/pred_tta.zip',

    '/media/hdd/Kaggle/Pneumothorax/Data/Preds/PANetResNet50_768_Fold5_ptx/pred_tta.zip',
    '/media/hdd/Kaggle/Pneumothorax/Data/Preds/PANetResNet50_768_Fold6_ptx/pred_tta.zip',
    '/media/hdd/Kaggle/Pneumothorax/Data/Preds/PANetResNet50_768_Fold4_ptx/pred_tta.zip',

    '/media/hdd/Kaggle/Pneumothorax/Data/Preds/EMANetResNet101_768_Fold0_ptx/pred_tta.zip',
]

weights = np.array([1] * 27)
assert len(weights) == len(fns)

root = '/media/hdd/Kaggle/Pneumothorax/Data/Preds'
handles = [ZipFile(os.path.join(root, fn)) for fn in fns]

image_ids, rles = [], []
pngs = ZipFile(os.path.join(root, fns[0])).namelist()
predictions = np.zeros((len(pngs), 1024, 1024), dtype=np.float16)
for i, png in enumerate(tqdm(pngs)):
    image_id = os.path.splitext(png)[0]
    p_ensemble = 0.0
    for handle, w in zip(handles, weights):
        with handle.open(png) as f:
            img = cv2.imdecode(np.frombuffer(f.read(), 'uint8'), 0)
            p = np.float32(img) / 255
            p_ensemble += p * w / np.sum(weights)
            predictions[i] = p_ensemble
    if i % 100 == 0:
        gc.collect()

gc.collect()

ths = 0.20,

mean_pred = predictions.copy()
mean_pred = (mean_pred > ths)
mean_pred = 255. * mean_pred

count = (mean_pred.reshape(mean_pred.shape[0], -1).sum(1) > 1).sum()
print('{:} non empty images ({:.2f}%)'.format(count, count / len(mean_pred)))
make_submission([os.path.splitext(x)[0] for x in pngs], mean_pred, os.path.join('/media/hdd/Kaggle/Pneumothorax/Output',
                                                                                'ens_seg_with_see.csv'))
del mean_pred
gc.collect()