graph [
  node_attrs_setting [
    name "cpu"
    type "resource"
    owner "node"
    distribution "uniform"
    dtype "int"
    generative "True"
    high "100"
    low "50"
  ]
  node_attrs_setting [
    name "max_cpu"
    type "extrema"
    owner "node"
    originator "cpu"
  ]
  link_attrs_setting [
    name "bw"
    type "resource"
    owner "link"
    distribution "uniform"
    dtype "int"
    generative "True"
    high "400"
    low "200"
  ]
  link_attrs_setting [
    name "max_bw"
    type "extrema"
    owner "link"
    originator "bw"
  ]
  topology___num_nodes "16"
  topology___type "fat_tree"
  topology___k "4"
  topology___wm_alpha "0.5"
  topology___wm_beta "0.2"
  output___save_dir "dataset/p_net"
  output___file_name "fat_tree_p_net.gml"
  node [
    id 0
    label "0"
    layer "core"
    cpu 90
    max_cpu 90
  ]
  node [
    id 1
    label "1"
    layer "core"
    cpu 65
    max_cpu 65
  ]
  node [
    id 2
    label "2"
    layer "core"
    cpu 95
    max_cpu 95
  ]
  node [
    id 3
    label "3"
    layer "core"
    cpu 58
    max_cpu 58
  ]
  node [
    id 4
    label "4"
    layer "aggregation"
    pod 0
    cpu 72
    max_cpu 72
  ]
  node [
    id 5
    label "5"
    layer "aggregation"
    pod 0
    cpu 93
    max_cpu 93
  ]
  node [
    id 6
    label "6"
    layer "edge"
    pod 0
    cpu 68
    max_cpu 68
  ]
  node [
    id 7
    label "7"
    layer "edge"
    pod 0
    cpu 61
    max_cpu 61
  ]
  node [
    id 8
    label "8"
    layer "host"
    pod 0
    cpu 90
    max_cpu 90
  ]
  node [
    id 9
    label "9"
    layer "host"
    pod 0
    cpu 57
    max_cpu 57
  ]
  node [
    id 10
    label "10"
    layer "host"
    pod 0
    cpu 84
    max_cpu 84
  ]
  node [
    id 11
    label "11"
    layer "host"
    pod 0
    cpu 99
    max_cpu 99
  ]
  node [
    id 12
    label "12"
    layer "aggregation"
    pod 1
    cpu 81
    max_cpu 81
  ]
  node [
    id 13
    label "13"
    layer "aggregation"
    pod 1
    cpu 61
    max_cpu 61
  ]
  node [
    id 14
    label "14"
    layer "edge"
    pod 1
    cpu 71
    max_cpu 71
  ]
  node [
    id 15
    label "15"
    layer "edge"
    pod 1
    cpu 97
    max_cpu 97
  ]
  node [
    id 16
    label "16"
    layer "host"
    pod 1
    cpu 81
    max_cpu 81
  ]
  node [
    id 17
    label "17"
    layer "host"
    pod 1
    cpu 76
    max_cpu 76
  ]
  node [
    id 18
    label "18"
    layer "host"
    pod 1
    cpu 70
    max_cpu 70
  ]
  node [
    id 19
    label "19"
    layer "host"
    pod 1
    cpu 87
    max_cpu 87
  ]
  node [
    id 20
    label "20"
    layer "aggregation"
    pod 2
    cpu 89
    max_cpu 89
  ]
  node [
    id 21
    label "21"
    layer "aggregation"
    pod 2
    cpu 53
    max_cpu 53
  ]
  node [
    id 22
    label "22"
    layer "edge"
    pod 2
    cpu 88
    max_cpu 88
  ]
  node [
    id 23
    label "23"
    layer "edge"
    pod 2
    cpu 54
    max_cpu 54
  ]
  node [
    id 24
    label "24"
    layer "host"
    pod 2
    cpu 92
    max_cpu 92
  ]
  node [
    id 25
    label "25"
    layer "host"
    pod 2
    cpu 93
    max_cpu 93
  ]
  node [
    id 26
    label "26"
    layer "host"
    pod 2
    cpu 89
    max_cpu 89
  ]
  node [
    id 27
    label "27"
    layer "host"
    pod 2
    cpu 88
    max_cpu 88
  ]
  node [
    id 28
    label "28"
    layer "aggregation"
    pod 3
    cpu 92
    max_cpu 92
  ]
  node [
    id 29
    label "29"
    layer "aggregation"
    pod 3
    cpu 83
    max_cpu 83
  ]
  node [
    id 30
    label "30"
    layer "edge"
    pod 3
    cpu 53
    max_cpu 53
  ]
  node [
    id 31
    label "31"
    layer "edge"
    pod 3
    cpu 55
    max_cpu 55
  ]
  node [
    id 32
    label "32"
    layer "host"
    pod 3
    cpu 74
    max_cpu 74
  ]
  node [
    id 33
    label "33"
    layer "host"
    pod 3
    cpu 54
    max_cpu 54
  ]
  node [
    id 34
    label "34"
    layer "host"
    pod 3
    cpu 96
    max_cpu 96
  ]
  node [
    id 35
    label "35"
    layer "host"
    pod 3
    cpu 56
    max_cpu 56
  ]
  edge [
    source 0
    target 4
    bw 295
    max_bw 295
  ]
  edge [
    source 0
    target 12
    bw 321
    max_bw 321
  ]
  edge [
    source 0
    target 20
    bw 231
    max_bw 231
  ]
  edge [
    source 0
    target 28
    bw 394
    max_bw 394
  ]
  edge [
    source 1
    target 4
    bw 280
    max_bw 280
  ]
  edge [
    source 1
    target 12
    bw 252
    max_bw 252
  ]
  edge [
    source 1
    target 20
    bw 250
    max_bw 250
  ]
  edge [
    source 1
    target 28
    bw 332
    max_bw 332
  ]
  edge [
    source 2
    target 5
    bw 263
    max_bw 263
  ]
  edge [
    source 2
    target 13
    bw 249
    max_bw 249
  ]
  edge [
    source 2
    target 21
    bw 239
    max_bw 239
  ]
  edge [
    source 2
    target 29
    bw 374
    max_bw 374
  ]
  edge [
    source 3
    target 5
    bw 336
    max_bw 336
  ]
  edge [
    source 3
    target 13
    bw 378
    max_bw 378
  ]
  edge [
    source 3
    target 21
    bw 215
    max_bw 215
  ]
  edge [
    source 3
    target 29
    bw 336
    max_bw 336
  ]
  edge [
    source 4
    target 6
    bw 345
    max_bw 345
  ]
  edge [
    source 4
    target 7
    bw 350
    max_bw 350
  ]
  edge [
    source 5
    target 6
    bw 317
    max_bw 317
  ]
  edge [
    source 5
    target 7
    bw 273
    max_bw 273
  ]
  edge [
    source 6
    target 8
    bw 385
    max_bw 385
  ]
  edge [
    source 6
    target 9
    bw 305
    max_bw 305
  ]
  edge [
    source 7
    target 10
    bw 310
    max_bw 310
  ]
  edge [
    source 7
    target 11
    bw 390
    max_bw 390
  ]
  edge [
    source 12
    target 14
    bw 283
    max_bw 283
  ]
  edge [
    source 12
    target 15
    bw 296
    max_bw 296
  ]
  edge [
    source 13
    target 14
    bw 243
    max_bw 243
  ]
  edge [
    source 13
    target 15
    bw 232
    max_bw 232
  ]
  edge [
    source 14
    target 16
    bw 226
    max_bw 226
  ]
  edge [
    source 14
    target 17
    bw 336
    max_bw 336
  ]
  edge [
    source 15
    target 18
    bw 276
    max_bw 276
  ]
  edge [
    source 15
    target 19
    bw 338
    max_bw 338
  ]
  edge [
    source 20
    target 22
    bw 240
    max_bw 240
  ]
  edge [
    source 20
    target 23
    bw 234
    max_bw 234
  ]
  edge [
    source 21
    target 22
    bw 260
    max_bw 260
  ]
  edge [
    source 21
    target 23
    bw 337
    max_bw 337
  ]
  edge [
    source 22
    target 24
    bw 270
    max_bw 270
  ]
  edge [
    source 22
    target 25
    bw 286
    max_bw 286
  ]
  edge [
    source 23
    target 26
    bw 398
    max_bw 398
  ]
  edge [
    source 23
    target 27
    bw 219
    max_bw 219
  ]
  edge [
    source 28
    target 30
    bw 256
    max_bw 256
  ]
  edge [
    source 28
    target 31
    bw 329
    max_bw 329
  ]
  edge [
    source 29
    target 30
    bw 268
    max_bw 268
  ]
  edge [
    source 29
    target 31
    bw 368
    max_bw 368
  ]
  edge [
    source 30
    target 32
    bw 281
    max_bw 281
  ]
  edge [
    source 30
    target 33
    bw 261
    max_bw 261
  ]
  edge [
    source 31
    target 34
    bw 398
    max_bw 398
  ]
  edge [
    source 31
    target 35
    bw 325
    max_bw 325
  ]
]
