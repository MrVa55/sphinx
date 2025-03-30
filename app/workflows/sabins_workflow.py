{
  "last_node_id": 52,
  "last_link_id": 111,
  "nodes": [
    {
      "id": 26,
      "type": "LTXVAddGuide",
      "pos": [
        1081.6207275390625,
        1194.662841796875
      ],
      "size": [
        315,
        162
      ],
      "flags": {},
      "order": 32,
      "mode": 0,
      "inputs": [
        {
          "name": "positive",
          "type": "CONDITIONING",
          "link": 59
        },
        {
          "name": "negative",
          "type": "CONDITIONING",
          "link": 60
        },
        {
          "name": "vae",
          "type": "VAE",
          "link": 74
        },
        {
          "name": "latent",
          "type": "LATENT",
          "link": 62
        },
        {
          "name": "image",
          "type": "IMAGE",
          "link": 63
        }
      ],
      "outputs": [
        {
          "name": "positive",
          "type": "CONDITIONING",
          "links": [
            66
          ],
          "slot_index": 0
        },
        {
          "name": "negative",
          "type": "CONDITIONING",
          "links": [
            67
          ],
          "slot_index": 1
        },
        {
          "name": "latent",
          "type": "LATENT",
          "links": [
            68
          ],
          "slot_index": 2
        }
      ],
      "properties": {
        "Node name for S&R": "LTXVAddGuide"
      },
      "widgets_values": [
        0,
        1
      ]
    },
    {
      "id": 19,
      "type": "LTXVPreprocess",
      "pos": [
        1083.0303955078125,
        1428.751953125
      ],
      "size": [
        315,
        58
      ],
      "flags": {},
      "order": 30,
      "mode": 0,
      "inputs": [
        {
          "name": "image",
          "type": "IMAGE",
          "link": 81
        }
      ],
      "outputs": [
        {
          "name": "output_image",
          "type": "IMAGE",
          "links": [
            63
          ],
          "slot_index": 0
        }
      ],
      "properties": {
        "Node name for S&R": "LTXVPreprocess"
      },
      "widgets_values": [
        40
      ]
    },
    {
      "id": 20,
      "type": "LTXVPreprocess",
      "pos": [
        1501.54248046875,
        1427.39453125
      ],
      "size": [
        315,
        58
      ],
      "flags": {},
      "order": 31,
      "mode": 0,
      "inputs": [
        {
          "name": "image",
          "type": "IMAGE",
          "link": 83
        }
      ],
      "outputs": [
        {
          "name": "output_image",
          "type": "IMAGE",
          "links": [
            69
          ],
          "slot_index": 0
        }
      ],
      "properties": {
        "Node name for S&R": "LTXVPreprocess"
      },
      "widgets_values": [
        40
      ]
    },
    {
      "id": 11,
      "type": "LTXVApplySTG",
      "pos": [
        1500.3453369140625,
        1079.3546142578125
      ],
      "size": [
        315,
        58
      ],
      "flags": {},
      "order": 16,
      "mode": 0,
      "inputs": [
        {
          "name": "model",
          "type": "MODEL",
          "link": 9
        }
      ],
      "outputs": [
        {
          "name": "model",
          "type": "MODEL",
          "links": [
            10
          ],
          "slot_index": 0
        }
      ],
      "properties": {
        "Node name for S&R": "LTXVApplySTG"
      },
      "widgets_values": [
        "14"
      ]
    },
    {
      "id": 7,
      "type": "SamplerCustomAdvanced",
      "pos": [
        2620.427978515625,
        1164.3114013671875
      ],
      "size": [
        355.20001220703125,
        106
      ],
      "flags": {},
      "order": 37,
      "mode": 0,
      "inputs": [
        {
          "name": "noise",
          "type": "NOISE",
          "link": 3
        },
        {
          "name": "guider",
          "type": "GUIDER",
          "link": 2
        },
        {
          "name": "sampler",
          "type": "SAMPLER",
          "link": 4
        },
        {
          "name": "sigmas",
          "type": "SIGMAS",
          "link": 79
        },
        {
          "name": "latent_image",
          "type": "LATENT",
          "link": 72
        }
      ],
      "outputs": [
        {
          "name": "output",
          "type": "LATENT",
          "links": [
            85
          ],
          "slot_index": 0
        },
        {
          "name": "denoised_output",
          "type": "LATENT",
          "links": null
        }
      ],
      "properties": {
        "Node name for S&R": "SamplerCustomAdvanced"
      },
      "widgets_values": []
    },
    {
      "id": 5,
      "type": "STGGuider",
      "pos": [
        2242.097900390625,
        1185.6693115234375
      ],
      "size": [
        315,
        146
      ],
      "flags": {},
      "order": 36,
      "mode": 0,
      "inputs": [
        {
          "name": "model",
          "type": "MODEL",
          "link": 10
        },
        {
          "name": "positive",
          "type": "CONDITIONING",
          "link": 7
        },
        {
          "name": "negative",
          "type": "CONDITIONING",
          "link": 8
        }
      ],
      "outputs": [
        {
          "name": "GUIDER",
          "type": "GUIDER",
          "links": [
            2
          ],
          "slot_index": 0
        }
      ],
      "properties": {
        "Node name for S&R": "STGGuider"
      },
      "widgets_values": [
        3,
        1,
        0.75
      ]
    },
    {
      "id": 13,
      "type": "EmptyLTXVLatentVideo",
      "pos": [
        676.87158203125,
        1749.301513671875
      ],
      "size": [
        315,
        130
      ],
      "flags": {},
      "order": 0,
      "mode": 0,
      "inputs": [],
      "outputs": [
        {
          "name": "LATENT",
          "type": "LATENT",
          "links": [
            62
          ],
          "slot_index": 0
        }
      ],
      "properties": {
        "Node name for S&R": "EmptyLTXVLatentVideo"
      },
      "widgets_values": [
        768,
        512,
        121,
        1
      ]
    },
    {
      "id": 15,
      "type": "CLIPTextEncode",
      "pos": [
        622.5274047851562,
        1480.2808837890625
      ],
      "size": [
        392.1722717285156,
        119.6710433959961
      ],
      "flags": {},
      "order": 15,
      "mode": 0,
      "inputs": [
        {
          "name": "clip",
          "type": "CLIP",
          "link": 19
        }
      ],
      "outputs": [
        {
          "name": "CONDITIONING",
          "type": "CONDITIONING",
          "links": [
            60
          ],
          "slot_index": 0
        }
      ],
      "properties": {
        "Node name for S&R": "CLIPTextEncode"
      },
      "widgets_values": [
        "shaky, glitchy, low quality, worst quality, deformed, distorted, disfigured, motion smear, motion artifacts, fused fingers, bad anatomy, weird hand, ugly, transition"
      ]
    },
    {
      "id": 31,
      "type": "LTXVScheduler",
      "pos": [
        1889.956787109375,
        1356.0611572265625
      ],
      "size": [
        315,
        154
      ],
      "flags": {},
      "order": 35,
      "mode": 0,
      "inputs": [
        {
          "name": "latent",
          "type": "LATENT",
          "shape": 7,
          "link": 78
        }
      ],
      "outputs": [
        {
          "name": "SIGMAS",
          "type": "SIGMAS",
          "links": [
            79
          ],
          "slot_index": 0
        }
      ],
      "properties": {
        "Node name for S&R": "LTXVScheduler"
      },
      "widgets_values": [
        20,
        2.05,
        0.95,
        true,
        0.1
      ]
    },
    {
      "id": 32,
      "type": "Note",
      "pos": [
        2258.57373046875,
        1423.3946533203125
      ],
      "size": [
        291.3345947265625,
        88
      ],
      "flags": {},
      "order": 1,
      "mode": 0,
      "inputs": [],
      "outputs": [],
      "properties": {},
      "widgets_values": [
        "For faster running times you can try setting cfg to 1."
      ],
      "color": "#432",
      "bgcolor": "#653"
    },
    {
      "id": 27,
      "type": "LTXVAddGuide",
      "pos": [
        1493.655517578125,
        1201.2786865234375
      ],
      "size": [
        315,
        162
      ],
      "flags": {},
      "order": 33,
      "mode": 0,
      "inputs": [
        {
          "name": "positive",
          "type": "CONDITIONING",
          "link": 66
        },
        {
          "name": "negative",
          "type": "CONDITIONING",
          "link": 67
        },
        {
          "name": "vae",
          "type": "VAE",
          "link": 75
        },
        {
          "name": "latent",
          "type": "LATENT",
          "link": 68
        },
        {
          "name": "image",
          "type": "IMAGE",
          "link": 69
        }
      ],
      "outputs": [
        {
          "name": "positive",
          "type": "CONDITIONING",
          "links": [
            70
          ],
          "slot_index": 0
        },
        {
          "name": "negative",
          "type": "CONDITIONING",
          "links": [
            71
          ],
          "slot_index": 1
        },
        {
          "name": "latent",
          "type": "LATENT",
          "links": [
            72,
            78
          ],
          "slot_index": 2
        }
      ],
      "properties": {
        "Node name for S&R": "LTXVAddGuide"
      },
      "widgets_values": [
        120,
        1
      ]
    },
    {
      "id": 34,
      "type": "ImageResizeKJ",
      "pos": [
        1092.6722412109375,
        1530.77978515625
      ],
      "size": [
        315,
        286
      ],
      "flags": {},
      "order": 27,
      "mode": 0,
      "inputs": [
        {
          "name": "image",
          "type": "IMAGE",
          "link": 111
        },
        {
          "name": "get_image_size",
          "type": "IMAGE",
          "shape": 7,
          "link": null
        },
        {
          "name": "width_input",
          "type": "INT",
          "shape": 7,
          "widget": {
            "name": "width_input"
          },
          "link": null
        },
        {
          "name": "height_input",
          "type": "INT",
          "shape": 7,
          "widget": {
            "name": "height_input"
          },
          "link": null
        }
      ],
      "outputs": [
        {
          "name": "IMAGE",
          "type": "IMAGE",
          "links": [
            81
          ],
          "slot_index": 0
        },
        {
          "name": "width",
          "type": "INT",
          "links": null
        },
        {
          "name": "height",
          "type": "INT",
          "links": null
        }
      ],
      "properties": {
        "Node name for S&R": "ImageResizeKJ"
      },
      "widgets_values": [
        768,
        512,
        "nearest-exact",
        false,
        2,
        0,
        0,
        "center"
      ]
    },
    {
      "id": 35,
      "type": "ImageResizeKJ",
      "pos": [
        1499.1163330078125,
        1531.5040283203125
      ],
      "size": [
        315,
        286
      ],
      "flags": {},
      "order": 29,
      "mode": 0,
      "inputs": [
        {
          "name": "image",
          "type": "IMAGE",
          "link": 110
        },
        {
          "name": "get_image_size",
          "type": "IMAGE",
          "shape": 7,
          "link": null
        },
        {
          "name": "width_input",
          "type": "INT",
          "shape": 7,
          "widget": {
            "name": "width_input"
          },
          "link": null
        },
        {
          "name": "height_input",
          "type": "INT",
          "shape": 7,
          "widget": {
            "name": "height_input"
          },
          "link": null
        }
      ],
      "outputs": [
        {
          "name": "IMAGE",
          "type": "IMAGE",
          "links": [
            83
          ],
          "slot_index": 0
        },
        {
          "name": "width",
          "type": "INT",
          "links": null
        },
        {
          "name": "height",
          "type": "INT",
          "links": null
        }
      ],
      "properties": {
        "Node name for S&R": "ImageResizeKJ"
      },
      "widgets_values": [
        768,
        512,
        "nearest-exact",
        false,
        2,
        0,
        0,
        "center"
      ]
    },
    {
      "id": 29,
      "type": "Note",
      "pos": [
        1510.7900390625,
        2206.3818359375
      ],
      "size": [
        304.03729248046875,
        88
      ],
      "flags": {},
      "order": 2,
      "mode": 0,
      "inputs": [],
      "outputs": [],
      "properties": {},
      "widgets_values": [
        "Last frame conditioning, the frame size shoudl match the generated video aspect ration."
      ],
      "color": "#432",
      "bgcolor": "#653"
    },
    {
      "id": 10,
      "type": "LTXVConditioning",
      "pos": [
        1881.857666015625,
        1204.921142578125
      ],
      "size": [
        315,
        78
      ],
      "flags": {},
      "order": 34,
      "mode": 0,
      "inputs": [
        {
          "name": "positive",
          "type": "CONDITIONING",
          "link": 70
        },
        {
          "name": "negative",
          "type": "CONDITIONING",
          "link": 71
        }
      ],
      "outputs": [
        {
          "name": "positive",
          "type": "CONDITIONING",
          "links": [
            7,
            87
          ],
          "slot_index": 0
        },
        {
          "name": "negative",
          "type": "CONDITIONING",
          "links": [
            8,
            88
          ],
          "slot_index": 1
        }
      ],
      "properties": {
        "Node name for S&R": "LTXVConditioning"
      },
      "widgets_values": [
        25
      ]
    },
    {
      "id": 37,
      "type": "LTXVCropGuides",
      "pos": [
        2688.18603515625,
        1336.5384521484375
      ],
      "size": [
        216.59999084472656,
        66
      ],
      "flags": {},
      "order": 38,
      "mode": 0,
      "inputs": [
        {
          "name": "positive",
          "type": "CONDITIONING",
          "link": 87
        },
        {
          "name": "negative",
          "type": "CONDITIONING",
          "link": 88
        },
        {
          "name": "latent",
          "type": "LATENT",
          "link": 85
        }
      ],
      "outputs": [
        {
          "name": "positive",
          "type": "CONDITIONING",
          "links": null
        },
        {
          "name": "negative",
          "type": "CONDITIONING",
          "links": null
        },
        {
          "name": "latent",
          "type": "LATENT",
          "links": [
            86
          ],
          "slot_index": 2
        }
      ],
      "properties": {
        "Node name for S&R": "LTXVCropGuides"
      },
      "widgets_values": []
    },
    {
      "id": 1,
      "type": "LoadImage",
      "pos": [
        1502.8370361328125,
        1844.201171875
      ],
      "size": [
        315,
        314
      ],
      "flags": {},
      "order": 3,
      "mode": 0,
      "inputs": [],
      "outputs": [
        {
          "name": "IMAGE",
          "type": "IMAGE",
          "links": [],
          "slot_index": 0
        },
        {
          "name": "MASK",
          "type": "MASK",
          "links": null
        }
      ],
      "properties": {
        "Node name for S&R": "LoadImage"
      },
      "widgets_values": [
        "00098-1867706314.jpeg",
        "image"
      ]
    },
    {
      "id": 16,
      "type": "CLIPLoader",
      "pos": [
        625.4815063476562,
        1078.2762451171875
      ],
      "size": [
        315,
        98
      ],
      "flags": {},
      "order": 4,
      "mode": 0,
      "inputs": [],
      "outputs": [
        {
          "name": "CLIP",
          "type": "CLIP",
          "links": [
            18,
            19
          ],
          "slot_index": 0
        }
      ],
      "properties": {
        "Node name for S&R": "CLIPLoader"
      },
      "widgets_values": [
        "t5/google_t5-v1_1-xxl_encoderonly-fp16.safetensors",
        "ltxv",
        "default"
      ]
    },
    {
      "id": 12,
      "type": "CheckpointLoaderSimple",
      "pos": [
        1080.441650390625,
        1033.5550537109375
      ],
      "size": [
        315,
        98
      ],
      "flags": {},
      "order": 5,
      "mode": 0,
      "inputs": [],
      "outputs": [
        {
          "name": "MODEL",
          "type": "MODEL",
          "links": [
            9
          ],
          "slot_index": 0
        },
        {
          "name": "CLIP",
          "type": "CLIP",
          "links": null
        },
        {
          "name": "VAE",
          "type": "VAE",
          "links": [
            73,
            74,
            75
          ],
          "slot_index": 2
        }
      ],
      "properties": {
        "Node name for S&R": "CheckpointLoaderSimple"
      },
      "widgets_values": [
        "LTXV/ltx-video-2b-v0.9.safetensors"
      ]
    },
    {
      "id": 38,
      "type": "CLIPTextEncode",
      "pos": [
        -1032.1314697265625,
        1741.3175048828125
      ],
      "size": [
        425.27801513671875,
        180.6060791015625
      ],
      "flags": {},
      "order": 18,
      "mode": 0,
      "inputs": [
        {
          "name": "clip",
          "label": "clip",
          "type": "CLIP",
          "link": 89
        }
      ],
      "outputs": [
        {
          "name": "CONDITIONING",
          "label": "CONDITIONING",
          "type": "CONDITIONING",
          "links": [
            101
          ],
          "slot_index": 0
        }
      ],
      "title": "CLIP Text Encode (Negative Prompt)",
      "properties": {
        "Node name for S&R": "CLIPTextEncode",
        "cnr_id": "comfy-core",
        "ver": "0.3.18"
      },
      "widgets_values": [
        "(worst quality, low quality:1.4), (bad anatomy), text, error, missing fingers, extra digit, fewer digits, cropped, jpeg artifacts, signature, watermark, username, blurry, deformed face"
      ],
      "color": "#322",
      "bgcolor": "#533"
    },
    {
      "id": 41,
      "type": "CheckpointLoaderSimple",
      "pos": [
        -986.9158325195312,
        1129.3365478515625
      ],
      "size": [
        315,
        98
      ],
      "flags": {},
      "order": 6,
      "mode": 0,
      "inputs": [],
      "outputs": [
        {
          "name": "MODEL",
          "label": "MODEL",
          "type": "MODEL",
          "links": [
            95,
            103
          ],
          "slot_index": 0
        },
        {
          "name": "CLIP",
          "label": "CLIP",
          "type": "CLIP",
          "links": [
            104
          ],
          "slot_index": 1
        },
        {
          "name": "VAE",
          "label": "VAE",
          "type": "VAE",
          "links": [
            91,
            93
          ],
          "slot_index": 2
        }
      ],
      "properties": {
        "Node name for S&R": "CheckpointLoaderSimple",
        "cnr_id": "comfy-core",
        "ver": "0.3.18",
        "models": [
          {
            "name": "dreamshaper_8.safetensors",
            "url": "https://civitai.com/api/download/models/128713?type=Model&format=SafeTensor&size=pruned&fp=fp16",
            "directory": "checkpoints"
          }
        ]
      },
      "widgets_values": [
        "photon_v1.safetensors"
      ]
    },
    {
      "id": 42,
      "type": "MarkdownNote",
      "pos": [
        -975.1666259765625,
        927.1097412109375
      ],
      "size": [
        312,
        136
      ],
      "flags": {},
      "order": 7,
      "mode": 0,
      "inputs": [],
      "outputs": [],
      "properties": {},
      "widgets_values": [
        "### Learn more about this workflow\n\n> [LoRA - ComfyUI_examples](https://comfyanonymous.github.io/ComfyUI_examples/lora/) — Overview\n> \n> [Multiple LoRAs - docs.comfy.org](https://docs.comfy.org/tutorials/basic/multiple-loras) — Detailed guide to using multiple LoRAs"
      ],
      "color": "#432",
      "bgcolor": "#653"
    },
    {
      "id": 43,
      "type": "CLIPTextEncode",
      "pos": [
        -1013.2985229492188,
        2349.085693359375
      ],
      "size": [
        425.27801513671875,
        180.6060791015625
      ],
      "flags": {},
      "order": 19,
      "mode": 0,
      "inputs": [
        {
          "name": "clip",
          "label": "clip",
          "type": "CLIP",
          "link": 94
        }
      ],
      "outputs": [
        {
          "name": "CONDITIONING",
          "label": "CONDITIONING",
          "type": "CONDITIONING",
          "links": [
            97
          ],
          "slot_index": 0
        }
      ],
      "properties": {
        "Node name for S&R": "CLIPTextEncode",
        "cnr_id": "comfy-core",
        "ver": "0.3.18"
      },
      "widgets_values": [
        "(worst quality, low quality:1.4), (bad anatomy), text, error, missing fingers, extra digit, fewer digits, cropped, jpeg artifacts, signature, watermark, username, blurry, deformed face"
      ],
      "color": "#232",
      "bgcolor": "#353"
    },
    {
      "id": 44,
      "type": "KSampler",
      "pos": [
        -561.110595703125,
        2058.683349609375
      ],
      "size": [
        306.40252685546875,
        274.4264831542969
      ],
      "flags": {},
      "order": 23,
      "mode": 0,
      "inputs": [
        {
          "name": "model",
          "label": "model",
          "type": "MODEL",
          "link": 95
        },
        {
          "name": "positive",
          "label": "positive",
          "type": "CONDITIONING",
          "link": 96
        },
        {
          "name": "negative",
          "label": "negative",
          "type": "CONDITIONING",
          "link": 97
        },
        {
          "name": "latent_image",
          "label": "latent_image",
          "type": "LATENT",
          "link": 98
        }
      ],
      "outputs": [
        {
          "name": "LATENT",
          "label": "LATENT",
          "type": "LATENT",
          "links": [
            92
          ],
          "slot_index": 0
        }
      ],
      "properties": {
        "Node name for S&R": "KSampler",
        "cnr_id": "comfy-core",
        "ver": "0.3.18"
      },
      "widgets_values": [
        959570447621611,
        "randomize",
        30,
        7,
        "dpmpp_2m",
        "karras",
        1
      ],
      "color": "#323",
      "bgcolor": "#535"
    },
    {
      "id": 49,
      "type": "EmptyLatentImage",
      "pos": [
        -560.9320678710938,
        2482.310302734375
      ],
      "size": [
        315,
        106
      ],
      "flags": {},
      "order": 8,
      "mode": 0,
      "inputs": [],
      "outputs": [
        {
          "name": "LATENT",
          "label": "LATENT",
          "type": "LATENT",
          "links": [
            98
          ],
          "slot_index": 0
        }
      ],
      "properties": {
        "Node name for S&R": "EmptyLatentImage",
        "cnr_id": "comfy-core",
        "ver": "0.3.18"
      },
      "widgets_values": [
        768,
        512,
        1
      ]
    },
    {
      "id": 52,
      "type": "SaveImage",
      "pos": [
        10.260437965393066,
        1525.9754638671875
      ],
      "size": [
        349.7459411621094,
        388.8688049316406
      ],
      "flags": {},
      "order": 26,
      "mode": 0,
      "inputs": [
        {
          "name": "images",
          "label": "images",
          "type": "IMAGE",
          "link": 108
        }
      ],
      "outputs": [],
      "properties": {
        "Node name for S&R": "SaveImage",
        "cnr_id": "comfy-core",
        "ver": "0.3.18"
      },
      "widgets_values": [
        "2loras_test_"
      ]
    },
    {
      "id": 45,
      "type": "KSampler",
      "pos": [
        -579.7395629882812,
        1525.9754638671875
      ],
      "size": [
        317.8104248046875,
        276.4546813964844
      ],
      "flags": {},
      "order": 22,
      "mode": 0,
      "inputs": [
        {
          "name": "model",
          "label": "model",
          "type": "MODEL",
          "link": 99
        },
        {
          "name": "positive",
          "label": "positive",
          "type": "CONDITIONING",
          "link": 100
        },
        {
          "name": "negative",
          "label": "negative",
          "type": "CONDITIONING",
          "link": 101
        },
        {
          "name": "latent_image",
          "label": "latent_image",
          "type": "LATENT",
          "link": 102
        }
      ],
      "outputs": [
        {
          "name": "LATENT",
          "label": "LATENT",
          "type": "LATENT",
          "links": [
            90
          ],
          "slot_index": 0
        }
      ],
      "properties": {
        "Node name for S&R": "KSampler",
        "cnr_id": "comfy-core",
        "ver": "0.3.18"
      },
      "widgets_values": [
        994165444986266,
        "randomize",
        30,
        7,
        "dpmpp_2m",
        "karras",
        1
      ],
      "color": "#323",
      "bgcolor": "#535"
    },
    {
      "id": 51,
      "type": "SaveImage",
      "pos": [
        28.889719009399414,
        2058.683349609375
      ],
      "size": [
        338.7420349121094,
        307.20758056640625
      ],
      "flags": {},
      "order": 28,
      "mode": 0,
      "inputs": [
        {
          "name": "images",
          "label": "images",
          "type": "IMAGE",
          "link": 107
        }
      ],
      "outputs": [],
      "properties": {
        "Node name for S&R": "SaveImage",
        "cnr_id": "comfy-core",
        "ver": "0.3.18"
      },
      "widgets_values": [
        "2loras_test_"
      ]
    },
    {
      "id": 28,
      "type": "Note",
      "pos": [
        1094.802490234375,
        2268.28271484375
      ],
      "size": [
        314.0157470703125,
        91.49161529541016
      ],
      "flags": {},
      "order": 9,
      "mode": 0,
      "inputs": [],
      "outputs": [],
      "properties": {},
      "widgets_values": [
        "First frame conditioning, the frame size shoudl match the generated video aspect ration."
      ],
      "color": "#432",
      "bgcolor": "#653"
    },
    {
      "id": 2,
      "type": "LoadImage",
      "pos": [
        1094.7757568359375,
        1884.470703125
      ],
      "size": [
        315,
        314
      ],
      "flags": {},
      "order": 10,
      "mode": 0,
      "inputs": [],
      "outputs": [
        {
          "name": "IMAGE",
          "type": "IMAGE",
          "links": [],
          "slot_index": 0
        },
        {
          "name": "MASK",
          "type": "MASK",
          "links": null
        }
      ],
      "properties": {
        "Node name for S&R": "LoadImage"
      },
      "widgets_values": [
        "7903825.png",
        "image"
      ]
    },
    {
      "id": 40,
      "type": "VAEDecode",
      "pos": [
        -211.11074829101562,
        2058.683349609375
      ],
      "size": [
        210,
        46
      ],
      "flags": {},
      "order": 25,
      "mode": 0,
      "inputs": [
        {
          "name": "samples",
          "label": "samples",
          "type": "LATENT",
          "link": 92
        },
        {
          "name": "vae",
          "label": "vae",
          "type": "VAE",
          "link": 93
        }
      ],
      "outputs": [
        {
          "name": "IMAGE",
          "label": "IMAGE",
          "type": "IMAGE",
          "links": [
            107,
            110
          ],
          "slot_index": 0
        }
      ],
      "properties": {
        "Node name for S&R": "VAEDecode",
        "cnr_id": "comfy-core",
        "ver": "0.3.18"
      }
    },
    {
      "id": 39,
      "type": "VAEDecode",
      "pos": [
        -250.87327575683594,
        1488.516357421875
      ],
      "size": [
        210,
        46
      ],
      "flags": {},
      "order": 24,
      "mode": 0,
      "inputs": [
        {
          "name": "samples",
          "label": "samples",
          "type": "LATENT",
          "link": 90
        },
        {
          "name": "vae",
          "label": "vae",
          "type": "VAE",
          "link": 91
        }
      ],
      "outputs": [
        {
          "name": "IMAGE",
          "label": "IMAGE",
          "type": "IMAGE",
          "links": [
            108,
            111
          ],
          "slot_index": 0
        }
      ],
      "properties": {
        "Node name for S&R": "VAEDecode",
        "cnr_id": "comfy-core",
        "ver": "0.3.18"
      }
    },
    {
      "id": 36,
      "type": "VHS_VideoCombine",
      "pos": [
        2649.404052734375,
        1612.633056640625
      ],
      "size": [
        315,
        544.6666870117188
      ],
      "flags": {},
      "order": 40,
      "mode": 0,
      "inputs": [
        {
          "name": "images",
          "type": "IMAGE",
          "shape": 7,
          "link": 84
        },
        {
          "name": "audio",
          "type": "AUDIO",
          "shape": 7,
          "link": null
        },
        {
          "name": "meta_batch",
          "type": "VHS_BatchManager",
          "shape": 7,
          "link": null
        },
        {
          "name": "vae",
          "type": "VAE",
          "shape": 7,
          "link": null
        }
      ],
      "outputs": [
        {
          "name": "Filenames",
          "type": "VHS_FILENAMES",
          "links": null
        }
      ],
      "properties": {
        "Node name for S&R": "VHS_VideoCombine"
      },
      "widgets_values": {
        "frame_rate": 25,
        "loop_count": 0,
        "filename_prefix": "LTX",
        "format": "video/h264-mp4",
        "pix_fmt": "yuv420p",
        "crf": 19,
        "save_metadata": true,
        "trim_to_audio": false,
        "pingpong": false,
        "save_output": true,
        "videopreview": {
          "hidden": false,
          "paused": false,
          "params": {
            "filename": "LTX_00004.mp4",
            "subfolder": "",
            "type": "output",
            "format": "video/h264-mp4",
            "frame_rate": 25,
            "workflow": "LTX_00004.png",
            "fullpath": "/workspace/ComfyUI/output/LTX_00004.mp4"
          }
        }
      }
    },
    {
      "id": 46,
      "type": "LoraLoader",
      "pos": [
        -989.667236328125,
        1285.4786376953125
      ],
      "size": [
        315,
        126
      ],
      "flags": {},
      "order": 17,
      "mode": 0,
      "inputs": [
        {
          "name": "model",
          "label": "model",
          "type": "MODEL",
          "link": 103
        },
        {
          "name": "clip",
          "label": "clip",
          "type": "CLIP",
          "link": 104
        }
      ],
      "outputs": [
        {
          "name": "MODEL",
          "label": "MODEL",
          "type": "MODEL",
          "links": [
            99
          ],
          "slot_index": 0
        },
        {
          "name": "CLIP",
          "label": "CLIP",
          "type": "CLIP",
          "links": [
            89,
            94,
            105,
            106
          ],
          "slot_index": 1
        }
      ],
      "properties": {
        "Node name for S&R": "LoraLoader",
        "cnr_id": "comfy-core",
        "ver": "0.3.18",
        "models": [
          {
            "name": "blindbox_v1_mix.safetensors",
            "url": "https://civitai.com/api/download/models/32988?type=Model&format=SafeTensor&size=full&fp=fp16",
            "directory": "loras"
          }
        ]
      },
      "widgets_values": [
        "burner_style_v1.safetensors",
        0.75,
        1
      ]
    },
    {
      "id": 47,
      "type": "CLIPTextEncode",
      "pos": [
        -1050.873291015625,
        1488.516357421875
      ],
      "size": [
        422.84503173828125,
        164.31304931640625
      ],
      "flags": {},
      "order": 20,
      "mode": 0,
      "inputs": [
        {
          "name": "clip",
          "label": "clip",
          "type": "CLIP",
          "link": 105
        }
      ],
      "outputs": [
        {
          "name": "CONDITIONING",
          "label": "CONDITIONING",
          "type": "CONDITIONING",
          "links": [
            100
          ],
          "slot_index": 0
        }
      ],
      "properties": {
        "Node name for S&R": "CLIPTextEncode",
        "cnr_id": "comfy-core",
        "ver": "0.3.18"
      },
      "widgets_values": [
        "a woman alone in a barren desolate parched landscape of scarcity and privation"
      ],
      "color": "#232",
      "bgcolor": "#353"
    },
    {
      "id": 48,
      "type": "CLIPTextEncode",
      "pos": [
        -1011.1104736328125,
        2058.683349609375
      ],
      "size": [
        422.84503173828125,
        164.31304931640625
      ],
      "flags": {},
      "order": 21,
      "mode": 0,
      "inputs": [
        {
          "name": "clip",
          "label": "clip",
          "type": "CLIP",
          "link": 106
        }
      ],
      "outputs": [
        {
          "name": "CONDITIONING",
          "label": "CONDITIONING",
          "type": "CONDITIONING",
          "links": [
            96
          ],
          "slot_index": 0
        }
      ],
      "properties": {
        "Node name for S&R": "CLIPTextEncode",
        "cnr_id": "comfy-core",
        "ver": "0.3.18"
      },
      "widgets_values": [
        " woman surrounded by lush growing green adundance in the company of friends"
      ],
      "color": "#232",
      "bgcolor": "#353"
    },
    {
      "id": 14,
      "type": "CLIPTextEncode",
      "pos": [
        617.918701171875,
        1220.501708984375
      ],
      "size": [
        400,
        200
      ],
      "flags": {},
      "order": 14,
      "mode": 0,
      "inputs": [
        {
          "name": "clip",
          "type": "CLIP",
          "link": 18
        }
      ],
      "outputs": [
        {
          "name": "CONDITIONING",
          "type": "CONDITIONING",
          "links": [
            59
          ],
          "slot_index": 0
        }
      ],
      "properties": {
        "Node name for S&R": "CLIPTextEncode"
      },
      "widgets_values": [
        "a slow, continuous transition between the a woman alone in a barren desolate parched landscape of scarcity and privation and the  woman surrounded by lush growing green adundance in the company of friends, timelapse, continuous motion, \n\n\n\n"
      ]
    },
    {
      "id": 50,
      "type": "EmptyLatentImage",
      "pos": [
        -578.1002197265625,
        1864.745849609375
      ],
      "size": [
        315,
        106
      ],
      "flags": {},
      "order": 11,
      "mode": 0,
      "inputs": [],
      "outputs": [
        {
          "name": "LATENT",
          "label": "LATENT",
          "type": "LATENT",
          "links": [
            102
          ],
          "slot_index": 0
        }
      ],
      "properties": {
        "Node name for S&R": "EmptyLatentImage",
        "cnr_id": "comfy-core",
        "ver": "0.3.18"
      },
      "widgets_values": [
        768,
        512,
        1
      ]
    },
    {
      "id": 9,
      "type": "KSamplerSelect",
      "pos": [
        2233.98828125,
        1065.9569091796875
      ],
      "size": [
        315,
        58
      ],
      "flags": {},
      "order": 12,
      "mode": 0,
      "inputs": [],
      "outputs": [
        {
          "name": "SAMPLER",
          "type": "SAMPLER",
          "links": [
            4
          ],
          "slot_index": 0
        }
      ],
      "properties": {
        "Node name for S&R": "KSamplerSelect"
      },
      "widgets_values": [
        "dpmpp_2m"
      ]
    },
    {
      "id": 17,
      "type": "VAEDecode",
      "pos": [
        2692.3857421875,
        1488.329345703125
      ],
      "size": [
        210,
        46
      ],
      "flags": {},
      "order": 39,
      "mode": 0,
      "inputs": [
        {
          "name": "samples",
          "type": "LATENT",
          "link": 86
        },
        {
          "name": "vae",
          "type": "VAE",
          "link": 73
        }
      ],
      "outputs": [
        {
          "name": "IMAGE",
          "type": "IMAGE",
          "links": [
            84
          ],
          "slot_index": 0
        }
      ],
      "properties": {
        "Node name for S&R": "VAEDecode"
      },
      "widgets_values": []
    },
    {
      "id": 8,
      "type": "RandomNoise",
      "pos": [
        1850.8992919921875,
        1055.1177978515625
      ],
      "size": [
        315,
        82
      ],
      "flags": {},
      "order": 13,
      "mode": 0,
      "inputs": [],
      "outputs": [
        {
          "name": "NOISE",
          "type": "NOISE",
          "links": [
            3
          ],
          "slot_index": 0
        }
      ],
      "properties": {
        "Node name for S&R": "RandomNoise"
      },
      "widgets_values": [
        288842117313765,
        "randomize"
      ]
    }
  ],
  "links": [
    [
      2,
      5,
      0,
      7,
      1,
      "GUIDER"
    ],
    [
      3,
      8,
      0,
      7,
      0,
      "NOISE"
    ],
    [
      4,
      9,
      0,
      7,
      2,
      "SAMPLER"
    ],
    [
      7,
      10,
      0,
      5,
      1,
      "CONDITIONING"
    ],
    [
      8,
      10,
      1,
      5,
      2,
      "CONDITIONING"
    ],
    [
      9,
      12,
      0,
      11,
      0,
      "MODEL"
    ],
    [
      10,
      11,
      0,
      5,
      0,
      "MODEL"
    ],
    [
      18,
      16,
      0,
      14,
      0,
      "CLIP"
    ],
    [
      19,
      16,
      0,
      15,
      0,
      "CLIP"
    ],
    [
      59,
      14,
      0,
      26,
      0,
      "CONDITIONING"
    ],
    [
      60,
      15,
      0,
      26,
      1,
      "CONDITIONING"
    ],
    [
      62,
      13,
      0,
      26,
      3,
      "LATENT"
    ],
    [
      63,
      19,
      0,
      26,
      4,
      "IMAGE"
    ],
    [
      66,
      26,
      0,
      27,
      0,
      "CONDITIONING"
    ],
    [
      67,
      26,
      1,
      27,
      1,
      "CONDITIONING"
    ],
    [
      68,
      26,
      2,
      27,
      3,
      "LATENT"
    ],
    [
      69,
      20,
      0,
      27,
      4,
      "IMAGE"
    ],
    [
      70,
      27,
      0,
      10,
      0,
      "CONDITIONING"
    ],
    [
      71,
      27,
      1,
      10,
      1,
      "CONDITIONING"
    ],
    [
      72,
      27,
      2,
      7,
      4,
      "LATENT"
    ],
    [
      73,
      12,
      2,
      17,
      1,
      "VAE"
    ],
    [
      74,
      12,
      2,
      26,
      2,
      "VAE"
    ],
    [
      75,
      12,
      2,
      27,
      2,
      "VAE"
    ],
    [
      78,
      27,
      2,
      31,
      0,
      "LATENT"
    ],
    [
      79,
      31,
      0,
      7,
      3,
      "SIGMAS"
    ],
    [
      81,
      34,
      0,
      19,
      0,
      "IMAGE"
    ],
    [
      83,
      35,
      0,
      20,
      0,
      "IMAGE"
    ],
    [
      84,
      17,
      0,
      36,
      0,
      "IMAGE"
    ],
    [
      85,
      7,
      0,
      37,
      2,
      "LATENT"
    ],
    [
      86,
      37,
      2,
      17,
      0,
      "LATENT"
    ],
    [
      87,
      10,
      0,
      37,
      0,
      "CONDITIONING"
    ],
    [
      88,
      10,
      1,
      37,
      1,
      "CONDITIONING"
    ],
    [
      89,
      46,
      1,
      38,
      0,
      "CLIP"
    ],
    [
      90,
      45,
      0,
      39,
      0,
      "LATENT"
    ],
    [
      91,
      41,
      2,
      39,
      1,
      "VAE"
    ],
    [
      92,
      44,
      0,
      40,
      0,
      "LATENT"
    ],
    [
      93,
      41,
      2,
      40,
      1,
      "VAE"
    ],
    [
      94,
      46,
      1,
      43,
      0,
      "CLIP"
    ],
    [
      95,
      41,
      0,
      44,
      0,
      "MODEL"
    ],
    [
      96,
      48,
      0,
      44,
      1,
      "CONDITIONING"
    ],
    [
      97,
      43,
      0,
      44,
      2,
      "CONDITIONING"
    ],
    [
      98,
      49,
      0,
      44,
      3,
      "LATENT"
    ],
    [
      99,
      46,
      0,
      45,
      0,
      "MODEL"
    ],
    [
      100,
      47,
      0,
      45,
      1,
      "CONDITIONING"
    ],
    [
      101,
      38,
      0,
      45,
      2,
      "CONDITIONING"
    ],
    [
      102,
      50,
      0,
      45,
      3,
      "LATENT"
    ],
    [
      103,
      41,
      0,
      46,
      0,
      "MODEL"
    ],
    [
      104,
      41,
      1,
      46,
      1,
      "CLIP"
    ],
    [
      105,
      46,
      1,
      47,
      0,
      "CLIP"
    ],
    [
      106,
      46,
      1,
      48,
      0,
      "CLIP"
    ],
    [
      107,
      40,
      0,
      51,
      0,
      "IMAGE"
    ],
    [
      108,
      39,
      0,
      52,
      0,
      "IMAGE"
    ],
    [
      110,
      40,
      0,
      35,
      0,
      "IMAGE"
    ],
    [
      111,
      39,
      0,
      34,
      0,
      "IMAGE"
    ]
  ],
  "groups": [
    {
      "id": 1,
      "title": "Group",
      "bounding": [
        -1146.5931396484375,
        950.3289184570312,
        1597.2054443359375,
        1653.958740234375
      ],
      "color": "#3f789e",
      "font_size": 24,
      "flags": {}
    }
  ],
  "config": {},
  "extra": {
    "ds": {
      "scale": 1.9487171000000014,
      "offset": [
        -2171.2457807615856,
        -1847.179133886771
      ]
    },
    "node_versions": {
      "comfy-core": "0.3.18"
    },
    "prompt": {
      "1": {
        "inputs": {
          "image": "end.jpg",
          "upload": "image"
        },
        "class_type": "LoadImage",
        "_meta": {
          "title": "Load Image"
        }
      },
      "2": {
        "inputs": {
          "image": "start.jpg",
          "upload": "image"
        },
        "class_type": "LoadImage",
        "_meta": {
          "title": "Load Image"
        }
      },
      "5": {
        "inputs": {
          "cfg": 3,
          "stg": 1,
          "rescale": 0.75,
          "model": [
            "11",
            0
          ],
          "positive": [
            "10",
            0
          ],
          "negative": [
            "10",
            1
          ]
        },
        "class_type": "STGGuider",
        "_meta": {
          "title": "🅛🅣🅧 STG Guider"
        }
      },
      "7": {
        "inputs": {
          "noise": [
            "8",
            0
          ],
          "guider": [
            "5",
            0
          ],
          "sampler": [
            "9",
            0
          ],
          "sigmas": [
            "31",
            0
          ],
          "latent_image": [
            "27",
            2
          ]
        },
        "class_type": "SamplerCustomAdvanced",
        "_meta": {
          "title": "SamplerCustomAdvanced"
        }
      },
      "8": {
        "inputs": {
          "noise_seed": 5
        },
        "class_type": "RandomNoise",
        "_meta": {
          "title": "RandomNoise"
        }
      },
      "9": {
        "inputs": {
          "sampler_name": "gradient_estimation"
        },
        "class_type": "KSamplerSelect",
        "_meta": {
          "title": "KSamplerSelect"
        }
      },
      "10": {
        "inputs": {
          "frame_rate": 25,
          "positive": [
            "27",
            0
          ],
          "negative": [
            "27",
            1
          ]
        },
        "class_type": "LTXVConditioning",
        "_meta": {
          "title": "LTXVConditioning"
        }
      },
      "11": {
        "inputs": {
          "block_indices": "14",
          "model": [
            "12",
            0
          ]
        },
        "class_type": "LTXVApplySTG",
        "_meta": {
          "title": "🅛🅣🅧 LTXV Apply STG"
        }
      },
      "12": {
        "inputs": {
          "ckpt_name": "ltx-video-2b-v0.9.5.safetensors"
        },
        "class_type": "CheckpointLoaderSimple",
        "_meta": {
          "title": "Load Checkpoint"
        }
      },
      "13": {
        "inputs": {
          "width": 768,
          "height": 512,
          "length": 121,
          "batch_size": 1
        },
        "class_type": "EmptyLTXVLatentVideo",
        "_meta": {
          "title": "EmptyLTXVLatentVideo"
        }
      },
      "14": {
        "inputs": {
          "text": "A donkey gracefully rides a surfboard, going from a fiery volcanic wave to a frozen, icy landscape. Initially, the dark brown donkey stands on a surfboard amidst a wave of lava, the intense orange flames illuminating its silhouette. The camera maintains a medium shot, slightly angled, capturing the donkey's determined expression. The scene shifts smoothly to a wide shot of the donkey on the same surfboard, now gliding across a frozen lake with scattered ice floes and snow-covered rocks. The lighting changes to a bright, clear winter day. The donkey's expression remains calm; its movement is smooth and controlled. The video is computer-generated imagery.\n\n\n\n\n\n\n",
          "clip": [
            "16",
            0
          ]
        },
        "class_type": "CLIPTextEncode",
        "_meta": {
          "title": "CLIP Text Encode (Prompt)"
        }
      },
      "15": {
        "inputs": {
          "text": "shaky, glitchy, low quality, worst quality, deformed, distorted, disfigured, motion smear, motion artifacts, fused fingers, bad anatomy, weird hand, ugly, transition",
          "clip": [
            "16",
            0
          ]
        },
        "class_type": "CLIPTextEncode",
        "_meta": {
          "title": "CLIP Text Encode (Prompt)"
        }
      },
      "16": {
        "inputs": {
          "clip_name": "t5xxl_fp16.safetensors",
          "type": "ltxv",
          "device": "default"
        },
        "class_type": "CLIPLoader",
        "_meta": {
          "title": "Load CLIP"
        }
      },
      "17": {
        "inputs": {
          "samples": [
            "37",
            2
          ],
          "vae": [
            "12",
            2
          ]
        },
        "class_type": "VAEDecode",
        "_meta": {
          "title": "VAE Decode"
        }
      },
      "19": {
        "inputs": {
          "img_compression": 40,
          "image": [
            "34",
            0
          ]
        },
        "class_type": "LTXVPreprocess",
        "_meta": {
          "title": "LTXVPreprocess"
        }
      },
      "20": {
        "inputs": {
          "img_compression": 40,
          "image": [
            "35",
            0
          ]
        },
        "class_type": "LTXVPreprocess",
        "_meta": {
          "title": "LTXVPreprocess"
        }
      },
      "26": {
        "inputs": {
          "frame_idx": 0,
          "strength": 1,
          "positive": [
            "14",
            0
          ],
          "negative": [
            "15",
            0
          ],
          "vae": [
            "12",
            2
          ],
          "latent": [
            "13",
            0
          ],
          "image": [
            "19",
            0
          ]
        },
        "class_type": "LTXVAddGuide",
        "_meta": {
          "title": "LTXVAddGuide"
        }
      },
      "27": {
        "inputs": {
          "frame_idx": 120,
          "strength": 1,
          "positive": [
            "26",
            0
          ],
          "negative": [
            "26",
            1
          ],
          "vae": [
            "12",
            2
          ],
          "latent": [
            "26",
            2
          ],
          "image": [
            "20",
            0
          ]
        },
        "class_type": "LTXVAddGuide",
        "_meta": {
          "title": "LTXVAddGuide"
        }
      },
      "31": {
        "inputs": {
          "steps": 20,
          "max_shift": 2.05,
          "base_shift": 0.95,
          "stretch": true,
          "terminal": 0.1,
          "latent": [
            "27",
            2
          ]
        },
        "class_type": "LTXVScheduler",
        "_meta": {
          "title": "LTXVScheduler"
        }
      },
      "34": {
        "inputs": {
          "width": 768,
          "height": 512,
          "upscale_method": "nearest-exact",
          "keep_proportion": false,
          "divisible_by": 2,
          "crop": "center",
          "image": [
            "2",
            0
          ]
        },
        "class_type": "ImageResizeKJ",
        "_meta": {
          "title": "Resize Image"
        }
      },
      "35": {
        "inputs": {
          "width": 768,
          "height": 512,
          "upscale_method": "nearest-exact",
          "keep_proportion": false,
          "divisible_by": 2,
          "crop": "center",
          "image": [
            "1",
            0
          ]
        },
        "class_type": "ImageResizeKJ",
        "_meta": {
          "title": "Resize Image"
        }
      },
      "36": {
        "inputs": {
          "frame_rate": 25,
          "loop_count": 0,
          "filename_prefix": "AnimateDiff",
          "format": "video/h264-mp4",
          "pix_fmt": "yuv420p",
          "crf": 19,
          "save_metadata": true,
          "pingpong": false,
          "save_output": true,
          "images": [
            "17",
            0
          ]
        },
        "class_type": "VHS_VideoCombine",
        "_meta": {
          "title": "Video Combine 🎥🅥🅗🅢"
        }
      },
      "37": {
        "inputs": {
          "positive": [
            "10",
            0
          ],
          "negative": [
            "10",
            1
          ],
          "latent": [
            "7",
            0
          ]
        },
        "class_type": "LTXVCropGuides",
        "_meta": {
          "title": "LTXVCropGuides"
        }
      }
    },
    "comfy_fork_version": "update_nodes@db0f122d",
    "VHS_latentpreview": false,
    "VHS_latentpreviewrate": 0,
    "VHS_MetadataImage": true,
    "VHS_KeepIntermediate": true
  },
  "version": 0.4
}