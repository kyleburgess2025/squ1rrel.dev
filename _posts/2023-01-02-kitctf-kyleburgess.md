---
layout: post
current: post
cover:  False
navigation: True
title: "Kyle Burgess Fun Times"
date: 2022-10-18 10:00:00
tags: [SekaiCTF, cryptography]
class: post-template
subclass: 'post'
author: kyleburgess2025
---

One of the more solvable challenges... completed in the silliest way possible.

Pretty much all of the thinking and coding was done by the brilliant Nisala Kalupahana. Major shoutout.
## Overview
- [Setup](#setup)
- [Brainstorming](#Brainstorming)
    - [Our Idea](#our-idea)
- [Implementation](#implementation)
- [Reflection](#reflection)

## Setup
We were provided with a [link](http://secure-image-encryption.ctf.sekai.team) to a website that accepts two input PNGs and returns them after encryption, as well as the encrypted flag. We were also given `server-player.py` which contains the script used to run the app. The exact encryption script is not provided.

## Brainstorming
We started by running a few photos through the website to see the output. The encrypted image was consistently black and white for the user-provided images, while the encrypted flag was colorful. We played around with a few images and did not find anything too exciting. However, we did notice that if we inputted a black screen with a single red pixel, the pixel would be moved to somewhere else in the image - hence, the "permutation" encryption. The pixel would be changed to gray; however, it would maintain its brightness value.

### Our Idea
*WHAT IF*... we make a blank 256 by 256 image with 255 pixels that are gray - one for each grayscale value excluding 0? So, we have a square 256 by 256 black image with a single stripe of gray where the first value has brightness 1, second has brightness 2, ..., and the last value has brightness 255. Now, when we run the encryption on it, each pixel will be permuted to a distinct, easily-identifiable location - just find the location with the same grayscale value! 

![Handy dandy graphic](/assets/sekai/kyleburgess2005/based_on_what.jpg)

 So, each pixel in location i is permuted to location j. In order to reverse the encryption of the flag, we will take the pixel in location j and place it in location i. Repeat this 256 times with stripes in different locations to reveal the entire flag. Easy!
## Implementation
First, we created the 256 images that we would use to decrypt the flag. We did not know the layout of the flag, so we decided to just make horizontal stripes across the canvas for each image. To do so, we used the Image package from PIL.
```py
from PIL import Image
import numpy as np
for i in range(256):
    img = np.zeros((256, 256), dtype=np.uint8)
    for j in range(256):
        img[i][j] = j
    
    Image.fromarray(img).save(f"images/{i}.png")
```
Superb. Time to encrypt these bad boys and decrypt the flag. Just post these to the website and analyze the results, right? **WRONG!** You silly goose, you forgot to consider the Captcha! There's probably a good way to do this fast. Instead, we decided to generate a bunch of Captcha tokens manually and submit those with each image pair (the website takes in 2 images per request... total pain). 

Ok, so here's the plan:
* We make a post request to the secure-image-encryption website with two files and a Captcha token.
* We save the three outputs (encrypted input files and encrypted flag) as numpy arrays.
* For each of the two encrypted input files:
    * Find nonzero entries in the array. The position of this entry in the array will be called newPos. The value of this entry will be the x-value of its original position. The y-value of its original position will be the y-value of the horizontal stripe the original image had. The original position of this array will be called oldPos.
    * Save the brightness value of the encrypted flag at position oldPos as the brightness of the decrypted flag at position newPos.
* Repeat above steps with different input files.

## The Code
```py
#   Open two images and append them to a list
images = []
rows = [i, j]
for row in rows:    
    with open(f"images/{row}.png", "rb") as img:
        images.append(('image', img.read()))

#   Get token from command line and send the request
token = input("")[1:-1]
resp = requests.post("http://secure-image-encryption.ctf.sekai.team/upload", files=images, data={"g-recaptcha-response": token})
resp = resp.text

#   Parse the response and get the two return images and the encrypted flag
reg = r'data:image/png;base64,(.*?)"'
return_images = []
for match in re.finditer(reg, resp):
    return_images.append(match[0][22:-1])
return_images = [Image.open(BytesIO(base64.b64decode(img))) for img in return_images]

#   Save the images
t = time.time()
return_images[0].save(f"outputs/{t}-{rows[0]}.png")
return_images[1].save(f"outputs/{t}-{rows[1]}.png")
return_images[2].save(f"outputs/{t}-flag.png")

#   Open the images as numpy arrays
imgs = {}
imgs[rows[0]] = np.asarray(return_images[0])
imgs[rows[1]] = np.asarray(return_images[1])
flag = np.asarray(return_images[2])

#   Open the output file where the flag image will be written
data = {}
with open("data.json") as f:
    data = json.load(f)

'''
If a pixel in the output is nonzero, the brightness of that pixel 
will be equal to the y-value of the pixel in the first image. The 
x value of the pixel in the first image will be equal to the row number
corresponding to the first image. So, in data, we will store the 
brightness of the pixel in the flag at that position as the value 
of the key corresponding to the location of the pixel in the first 
image
'''
for row, img in imgs.items():
    for i in range(256):
        for j in range(256):
            if img[i][j] != 0:
                loc = f"{row},{img[i][j]}"
                data[loc] = f"{flag[i][j]}"

#   Write the data to the file. Also, Nisala's silly progress statement.
print(f"Extracted: {(len(data.keys()) / 65536) * 100}%")
with open("data.json", "w") as f:
    f.write(json.dumps(data))
```

Now, run this file with a CAPTCHA token as a parameter 256/2 (you do the math, it's 1 AM) times (my 2048 skills just kicked in; 256/2=128). As you can imagine, this would take ages. We decided to skip rows - after all, certainly we don't need every row to read the flag! We soon figured out the flag was written in diagonal text across the image. To speed things up, we could have started only decrypting the diagonal portion of the flag image rather than continuing to decrypt horizontal rows, but where's the fun in that? After about twenty minutes of running our script over and over, we were able to reveal the beautiful image:

![Converted Flag](/assets/sekai/kyleburgess2005/convertedflag.webp)

And... we're done! If you're wondering how we got the image from the JSON file:

```py
import json
import numpy as np
from PIL import Image

data = {}
with open("data.json") as f:
    data = json.load(f)

flag = np.zeros((256, 256), dtype=np.uint8)
for i in range(256):
    for j in range(256):
        loc = f"{i},{j}"
        if loc in data:
            flag[i][j] = int(data[loc])

Image.fromarray(flag).save("convertedflag.png")
```

## Reflection
Jeez, this was an interesting challenge. As someone who is new to CTFs, I really liked that this required less background knowledge of encryption methods and more creative thinking. A decent chunk of the solving process was spent just messing around with the image encryptor and figuring out how it works so we could reverse it. I would love to see more challenges like this in the future.

Again, massive shoutout to Nisala for completing the challenge and helping me understand it along the way. 
