import pandas as pd
from PIL import Image

def loadImage(fileName, resize=False, format="RGB"):
  image = Image.open(fileName)
  return imageToArray(image, format, resize)


def squareAndResizeImage(image, resize):
  import PIL

  w, h = image.size
  d = min(w, h)
  image = image.crop( (0, 0, d, d) ).resize( (resize, resize), resample=PIL.Image.LANCZOS )
  
  return image

def imageToArray(image, format, resize):
  import skimage
  import skimage.io
  import numpy as np

  w, h = image.size
  if resize:
    image = squareAndResizeImage(image, resize)

  image = image.convert('RGB')
  rgb = np.array(image)
  if format == "RGB":
    rgb = rgb.astype(int)
    return rgb.transpose([1,0,2])
  elif format == "Lab":
    lab = skimage.color.rgb2lab(rgb)
    return lab.transpose([1,0,2])
  else:
    raise Exception(f"Unknown format {format}")


imageCache = {}


def getTileImage(fileName, size):
  key = f"{fileName}-{size}px"

  if key not in imageCache:
    imageCache[key] = squareAndResizeImage(Image.open(fileName), size)

  return imageCache[key]



def isImageFile(file):
  for ext in [".jpg", ".jpeg", ".png"]:
    if file.endswith(ext) or file.endswith(ext.upper()):
      return True

  return False

def listTileImagesInPath(path):
  from os import listdir
  from os.path import isfile, join

  files = []
  for f in listdir(path + "/"):
    file = join(path + "/", f)
    if isfile(file) and isImageFile(file):
      files.append(file)

  return files


tada = "\N{PARTY POPPER}"


def run_test_case_1b(green_pixel):
  if len(green_pixel) != 3:
    print("\N{CROSS MARK} `green_pixel` does not contain a pixel.")
    return
  else:
    print("\u2705 `green_pixel` looks like a pixel!")

  if green_pixel[0] == 0 and green_pixel[1] == 255 and green_pixel[2] == 0:
    print("\u2705 `green_pixel` is a green pixel!")
    print(f"{tada} All tests passed! {tada}")
  else:
    print("\N{CROSS MARK} `green_pixel` looks like a pixel, but it's not green! Check your (x, y) coordinates.")
    return


def run_test_case_2d(df):
  if len(df) != 3:
    print("\N{CROSS MARK} `df` should only include three observations.")
    return
  else:
    print("\u2705 `df` contains the correct number of observations.")

  for colName in ['r', 'g', 'b', 'x', 'y']:
    if colName not in df:
      print(f"\N{CROSS MARK} `df` must contain a variable (column) `{colName}`.")
      return

  if df["r"].sum() == 510 and df["b"].sum() == 510 and df["g"].sum() == 255 and df["x"].sum() == 3 and df["y"].sum() == 0:
    print("\u2705 `df` contains the expected data!")
    print(f"{tada} All tests passed! {tada}")
  else:
    print("\N{CROSS MARK} `df` has incorrect data.")


def run_test_case_2e(df):
  if len(df) != 9:
    print("\N{CROSS MARK} `df` should only include nine observations.")
    return
  else:
    print("\u2705 `df` contains the correct number of observations.")

  for colName in ['r', 'g', 'b', 'x', 'y']:
    if colName not in df:
      print(f"\N{CROSS MARK} `df` must contain a variable (column) `{colName}`.")
      return

  if df["r"].sum() == 1294 and df["b"].sum() == 1141 and df["g"].sum() == 1146 and df["x"].sum() == 9 and df["y"].sum() == 9:
    print("\u2705 `df` contains the expected data!")
    print(f"{tada} All tests passed! {tada}")
  else:
    print("\N{CROSS MARK} `df` has incorrect data.")


def run_test_case_3(f):
  df = f("sample.png")
  
  if not isinstance(df, pd.DataFrame):
    print(f"\N{CROSS MARK} Your function must return a DataFrame.")
    return


  for colName in ['r', 'g', 'b', 'x', 'y']:
    if colName not in df:
      print(f"\N{CROSS MARK} `df` must contain a variable (column) `{colName}`.")
      return

  print("\u2705 `df` looks good!")
  print(f"{tada} All tests passed! {tada}")


def run_test_case_4(findAverageColor):
  pixelData = [
    [ [0, 0, 0], [0, 0, 0], [3, 6, 9] ]
  ]
  result = findAverageColor(pixelData)
  
  for colName in ['avg_r', 'avg_g', 'avg_b']:
    if colName not in result:
      print(f"\N{CROSS MARK} Dictionary must contain the key `{colName}`.")
      return
    else:
      print(f"\u2705 Dictionary contain the key `{colName}`.")

  if result["avg_r"] == 1 and result["avg_g"] == 2 and result["avg_b"] == 3:
    print("\u2705 Looks good!")
    print(f"{tada} All tests passed! {tada}")
  else:
    print(f"\N{CROSS MARK} Dictionary data is incorrect.")


def run_test_case_6(findAverageColorInRegion):
  pixelData = [
    # [0]           [1]           [2]           [3]
    [ [ 0,  0,  0], [ 0,  0,  0], [ 0,  0,  0], [ 0,  0,  0] ],  # [0]
    [ [ 0,  0,  0], [ 0,  0,  0], [ 0,  0,  0], [30, 60, 90] ],  # [1]
    [ [ 0,  0,  0], [ 0,  0,  0], [30, 60, 90], [30, 60, 90] ],  # [2]
    [ [ 0,  0,  0], [30, 60, 90], [30, 60, 90], [30, 60, 90] ],  # [3]
    [ [30, 60, 90], [30, 60, 90], [30, 60, 90], [30, 60, 90] ],  # [4]
    [ [30, 60, 90], [30, 60, 90], [30, 60, 90], [ 0,  0,  0] ],  # [5]
    [ [30, 60, 90], [30, 60, 90], [ 0,  0,  0], [ 0,  0,  0] ],  # [6]
    [ [30, 60, 90], [ 0,  0,  0], [ 0,  0,  0], [ 0,  0,  0] ],  # [7]
    [ [ 0,  0,  0], [ 0,  0,  0], [ 0,  0,  0], [ 0,  0,  0] ],  # [8]
  ]

  def TEST_findAverageColorInRegion(f, x, y, w, h, expected):
    result = f(pixelData, x, y, w, h)
    if result["avg_r"] != expected[0] or result["avg_g"] != expected[1] or result["avg_b"] != expected[2]:
      print(f"\N{CROSS MARK} Unexpected result: box_x = {x}, box_y = {y}, box_width = {w}, box_height={h} did not have the expected value.")
      
      r = result["avg_r"]
      g = result["avg_g"]
      b = result["avg_b"]
      print(f"  Your Result: avg_r={r}, avg_g={g}, avg_b={b}")

      r = expected[0]
      g = expected[1]
      b = expected[2]
      print(f"  Expected Result: avg_r={r}, avg_g={g}, avg_b={b}")
      return False
    else:
      print(f"\u2705 Test case with box_x = {x}, box_y = {y}, box_width = {w}, box_height={h} found returned the correct average color.")
      return True

  r = TEST_findAverageColorInRegion(findAverageColorInRegion, 0, 0, 2, 2, [0, 0, 0])
  if not r: return

  r = TEST_findAverageColorInRegion(findAverageColorInRegion, 2, 0, 2, 2, [7.5, 15, 22.5])
  if not r: return

  r = TEST_findAverageColorInRegion(findAverageColorInRegion, 2, 2, 2, 2, [30, 60, 90])
  if not r: return

  r = TEST_findAverageColorInRegion(findAverageColorInRegion, 5, 1, 2, 2, [90/4, 180/4, 270/4])
  if not r: return

  r = TEST_findAverageColorInRegion(findAverageColorInRegion, 5, 1, 4, 2, [90/8, 180/8, 270/8])
  if not r: return

  r = TEST_findAverageColorInRegion(findAverageColorInRegion, 5, 1, 4, 3, [90/12, 180/12, 270/12])
  if not r: return

  print(f"{tada} All tests passed! {tada}")




def run_test_case_7(findBestTile):
  real_df = pd.DataFrame([
      {'file': 'test.png', 'r': 47.19722525581813, 'g': 49.03421116311881, 'b': 38.60877549417687},
      {'file': 'test2.png', 'r': 54.24409328969397, 'g': 59.3141053878179, 'b': 52.97987993308968},
      {'file': 'test3.png', 'r': 46.41423991872082, 'g': 47.89200069370779, 'b': 37.011986112075455}
  ])

  try:
    bestMatch = findBestTile(real_df, 0, 0, 0)
    assert(type(bestMatch) == type(pd.DataFrame())), "findBestMatch must return a DataFrame"
    assert(len(bestMatch) == 1), "findBestMatch must return exactly one best match"
    assert(bestMatch['file'].values[0] == 'test3.png'), "findBestMatch did not return the best match for test (r=0, g=0, b=0)"
    print(f"\u2705 Test case #1 (r=0, g=0, b=0) passed!")

    bestMatch = findBestTile(real_df, 47, 49, 38)
    assert(bestMatch['file'].values[0] == 'test.png'), "findBestMatch did not return the best match for test (r=47, g=49, b=38)"
    print(f"\u2705 Test case #1 (r=47, g=49, b=38) passed!")

    bestMatch = findBestTile(real_df, 54, 49, 38)
    assert(bestMatch['file'].values[0] == 'test.png'), "findBestMatch did not return the best match for test (r=54, g=49, b=38)"
    print(f"\u2705 Test case #1 (r=54, g=49, b=38) passed!")

    bestMatch = findBestTile(real_df, 54, 49, 52)
    assert(bestMatch['file'].values[0] == 'test2.png'), "findBestMatch did not return the best match for test (r=54, g=49, b=52)"
    print(f"\u2705 Test case #1 (r=54, g=49, b=52) passed!")

    bestMatch = findBestTile(real_df, -100, -100, -100)
    assert(bestMatch['file'].values[0] == 'test3.png'), "findBestMatch did not return the best match for test (r=-100, g=-100, b=-100)"
    print(f"\u2705 Test case #1 (r=-100, g=-100, b=-100) passed!")

    print(f"{tada} All tests passed! {tada}")

  except AssertionError as e:
    print(f"\N{CROSS MARK} {e}.")

  


def createImageDataFrame(width, height):
  import random

  data = []
  for x in range(width):
    for y in range(height):
      data.append( {"x": x, "y": y, "r": random.randint(0, 255), "g": random.randint(0, 255), "b": random.randint(0, 255)} )
  
  return pd.DataFrame(data)
