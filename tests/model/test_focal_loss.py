import random
import pytest
import torch

from model.model import retina_resnet50
from model.loss import RetinaLoss
from data_loader.data_loaders import load_sample_coco_dls
from utils.box_utils import remove_zero_area_bboxes

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
BATCH_SIZE = 2
NUM_CLASSES = 6
NUM_ANCHORS = 9


@pytest.fixture(scope="module")
def init_512x512_dummy_data():
    return torch.randn((BATCH_SIZE, 3, 512, 512))


@pytest.fixture(scope="module")
def init_dummy_target_boxes_and_labels():
    num_items = [random.randint(0, 7) for _ in range(BATCH_SIZE)]
    bboxes = [torch.randn((num_items[i], 4)) for i in range(BATCH_SIZE)]
    labels = [
        torch.randint(high=NUM_CLASSES, size=(num_items[i], 1))
        for i in range(BATCH_SIZE)
    ]
    return labels, bboxes


@pytest.fixture(scope="module")
def init_sample_coco_one_batch():
    dls = load_sample_coco_dls(bs=BATCH_SIZE, seed=32)
    batch = dls.one_batch()
    imgs, bboxes, lbls = batch
    return imgs, lbls, bboxes


@pytest.mark.skip("Focus on sample test")
def test_retina_loss_w_retina_res50_on_dummy_data(
    init_512x512_dummy_data, init_dummy_target_boxes_and_labels
):
    data = init_512x512_dummy_data
    lbls, bboxes = init_dummy_target_boxes_and_labels

    model = retina_resnet50(num_classes=NUM_CLASSES)
    crit = RetinaLoss(num_classes=NUM_CLASSES)

    outputs = model(data)
    loss = crit(outputs, bboxes, lbls)
    assert not torch.isnan(loss)


def test_retina_loss_w_retina_res50_on_sample_coco_batch(init_sample_coco_one_batch):
    data, lbls, bboxes = init_sample_coco_one_batch
    assert len(bboxes) == BATCH_SIZE
    assert len(lbls) == BATCH_SIZE
    assert len(data) == BATCH_SIZE

    model = retina_resnet50(num_classes=NUM_CLASSES).to(DEVICE)
    crit = RetinaLoss(num_classes=NUM_CLASSES).to(DEVICE)

    outputs = model(data)
    loss = crit(outputs, bboxes, lbls)
    print(f"FINAL LOSS: {loss.item()}")

    assert not torch.isnan(loss)