# python 3.6
import numpy as np
import cv2


def get_data(imageFile):
    img = np.load(imageFile)
    return img


def global_threshold(data):
    Tmax = np.max(data)
    Tmin = np.min(data)

    T = (Tmax + Tmin) / 2

    while True:
        TF = np.mean(data[data > T])
        TB = np.mean(data[data <= T])
        T_new = (TF + TB) / 2
        if (np.abs(T_new - T) < 1e-4):
            break
        T = T_new

    mask = data.copy()
    mask[data > T_new] = 1
    mask[data < T_new] = 0

    return mask


def get_mask(data):

    mask_0 = global_threshold(data)

    # 闭运算
    mask_1 = 1 - mask_0  # 取反（肺白）
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    mask_dl1 = cv2.dilate(mask_1, kernel)  # 膨胀
    mask_er1 = cv2.erode(mask_dl1, kernel)  # 腐蚀

    # 提取最大连通域
    mask_2 = 1 - mask_er1    # 取反（肺黑）
    mask_uint8 = mask_2.astype(np.uint8) * 255  # 转换为uint8

    contours, _ = cv2.findContours(
        mask_uint8, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)  # 寻找连通域

    # 第2,3连通域即为左右肺
    indexs = [cv2.contourArea(cnt) for cnt in contours]

    if (len(indexs) < 3):
        return np.zeros_like(data)  # 若小于3个连通域则说明无肺
    l, r = np.argsort(indexs)[-3:-1]

    mask_3 = np.zeros([mask_1.shape[0], mask_1.shape[1]])
    cv2.drawContours(mask_3, contours, l, 1, cv2.FILLED)
    cv2.drawContours(mask_3, contours, r, 1, cv2.FILLED)

    # 闭运算

    mask_4 = mask_3
    for i in range(3):
        kernel2 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (10, 10))
        mask_dl2 = cv2.dilate(mask_4, kernel2)  # 膨胀
        mask_er2 = cv2.erode(mask_dl2, kernel2)  # 腐蚀
        mask_4 = mask_er2

    return mask_4


def gen_mask(data):
    mask = np.zeros_like(data)
    for i in range(data.shape[0]):
        mask[i] = get_mask(data[i])
    return mask


"""
def show_mask(mask):
    plt.imshow(mask * 255, cmap='gray')
    plt.show()
"""

if __name__ == "__main__":

    """
    for i in range(5):
        raw_CT = get_data('./output/' + str(i) + '.npy')
        plt.subplot(1, 2, 1)
        plt.imshow(raw_CT, cmap='gray')

        mask = get_mask(raw_CT)
        plt.subplot(1, 2, 2)
        plt.imshow(mask * 255, cmap='gray')
        plt.savefig('./output/' + str(i) + '.jpg')
        plt.show()


    if Old_versions:
        # 闭运算整形
        kernel2 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (10, 10))
        mask_3 = cv2.dilate(mask_2, kernel2)  # 膨胀
        mask_4 = cv2.erode(mask_3, kernel2)  # 腐蚀
        show_mask(mask_4)

        # 最大连通域
        max_idx = np.argmax([cv2.contourArea(cnt)
                            for cnt in contours])  # 最大连通域index
        mask_4 = np.zeros([mask_3.shape[0], mask_3.shape[1]])
        cv2.drawContours(mask_4, contours, max_idx, 1, cv2.FILLED)  # 最大连通域填充
        mask_3 = mask_4 * mask_3
        show_mask(mask_4)
        show_mask(mask_3)
    """

    pass
