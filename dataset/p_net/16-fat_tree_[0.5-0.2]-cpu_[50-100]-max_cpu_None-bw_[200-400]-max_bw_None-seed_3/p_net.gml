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
    cpu 92
    max_cpu 92
  ]
  node [
    id 1
    label "1"
    layer "core"
    cpu 74
    max_cpu 74
  ]
  node [
    id 2
    label "2"
    layer "core"
    cpu 53
    max_cpu 53
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
    cpu 50
    max_cpu 50
  ]
  node [
    id 5
    label "5"
    layer "aggregation"
    pod 0
    cpu 71
    max_cpu 71
  ]
  node [
    id 6
    label "6"
    layer "edge"
    pod 0
    cpu 69
    max_cpu 69
  ]
  node [
    id 7
    label "7"
    layer "edge"
    pod 0
    cpu 60
    max_cpu 60
  ]
  node [
    id 8
    label "8"
    layer "host"
    pod 0
    cpu 93
    max_cpu 93
  ]
  node [
    id 9
    label "9"
    layer "host"
    pod 0
    cpu 91
    max_cpu 91
  ]
  node [
    id 10
    label "10"
    layer "host"
    pod 0
    cpu 60
    max_cpu 60
  ]
  node [
    id 11
    label "11"
    layer "host"
    pod 0
    cpu 71
    max_cpu 71
  ]
  node [
    id 12
    label "12"
    layer "aggregation"
    pod 1
    cpu 88
    max_cpu 88
  ]
  node [
    id 13
    label "13"
    layer "aggregation"
    pod 1
    cpu 82
    max_cpu 82
  ]
  node [
    id 14
    label "14"
    layer "edge"
    pod 1
    cpu 70
    max_cpu 70
  ]
  node [
    id 15
    label "15"
    layer "edge"
    pod 1
    cpu 94
    max_cpu 94
  ]
  node [
    id 16
    label "16"
    layer "host"
    pod 1
    cpu 79
    max_cpu 79
  ]
  node [
    id 17
    label "17"
    layer "host"
    pod 1
    cpu 89
    max_cpu 89
  ]
  node [
    id 18
    label "18"
    layer "host"
    pod 1
    cpu 64
    max_cpu 64
  ]
  node [
    id 19
    label "19"
    layer "host"
    pod 1
    cpu 76
    max_cpu 76
  ]
  node [
    id 20
    label "20"
    layer "aggregation"
    pod 2
    cpu 67
    max_cpu 67
  ]
  node [
    id 21
    label "21"
    layer "aggregation"
    pod 2
    cpu 76
    max_cpu 76
  ]
  node [
    id 22
    label "22"
    layer "edge"
    pod 2
    cpu 72
    max_cpu 72
  ]
  node [
    id 23
    label "23"
    layer "edge"
    pod 2
    cpu 52
    max_cpu 52
  ]
  node [
    id 24
    label "24"
    layer "host"
    pod 2
    cpu 52
    max_cpu 52
  ]
  node [
    id 25
    label "25"
    layer "host"
    pod 2
    cpu 51
    max_cpu 51
  ]
  node [
    id 26
    label "26"
    layer "host"
    pod 2
    cpu 76
    max_cpu 76
  ]
  node [
    id 27
    label "27"
    layer "host"
    pod 2
    cpu 55
    max_cpu 55
  ]
  node [
    id 28
    label "28"
    layer "aggregation"
    pod 3
    cpu 90
    max_cpu 90
  ]
  node [
    id 29
    label "29"
    layer "aggregation"
    pod 3
    cpu 96
    max_cpu 96
  ]
  node [
    id 30
    label "30"
    layer "edge"
    pod 3
    cpu 83
    max_cpu 83
  ]
  node [
    id 31
    label "31"
    layer "edge"
    pod 3
    cpu 79
    max_cpu 79
  ]
  node [
    id 32
    label "32"
    layer "host"
    pod 3
    cpu 92
    max_cpu 92
  ]
  node [
    id 33
    label "33"
    layer "host"
    pod 3
    cpu 74
    max_cpu 74
  ]
  node [
    id 34
    label "34"
    layer "host"
    pod 3
    cpu 57
    max_cpu 57
  ]
  node [
    id 35
    label "35"
    layer "host"
    pod 3
    cpu 93
    max_cpu 93
  ]
  edge [
    source 0
    target 4
    bw 233
    max_bw 233
  ]
  edge [
    source 0
    target 12
    bw 323
    max_bw 323
  ]
  edge [
    source 0
    target 20
    bw 279
    max_bw 279
  ]
  edge [
    source 0
    target 28
    bw 376
    max_bw 376
  ]
  edge [
    source 1
    target 4
    bw 237
    max_bw 237
  ]
  edge [
    source 1
    target 12
    bw 220
    max_bw 220
  ]
  edge [
    source 1
    target 20
    bw 294
    max_bw 294
  ]
  edge [
    source 1
    target 28
    bw 249
    max_bw 249
  ]
  edge [
    source 2
    target 5
    bw 349
    max_bw 349
  ]
  edge [
    source 2
    target 13
    bw 327
    max_bw 327
  ]
  edge [
    source 2
    target 21
    bw 228
    max_bw 228
  ]
  edge [
    source 2
    target 29
    bw 319
    max_bw 319
  ]
  edge [
    source 3
    target 5
    bw 254
    max_bw 254
  ]
  edge [
    source 3
    target 13
    bw 200
    max_bw 200
  ]
  edge [
    source 3
    target 21
    bw 392
    max_bw 392
  ]
  edge [
    source 3
    target 29
    bw 218
    max_bw 218
  ]
  edge [
    source 4
    target 6
    bw 316
    max_bw 316
  ]
  edge [
    source 4
    target 7
    bw 391
    max_bw 391
  ]
  edge [
    source 5
    target 6
    bw 365
    max_bw 365
  ]
  edge [
    source 5
    target 7
    bw 384
    max_bw 384
  ]
  edge [
    source 6
    target 8
    bw 384
    max_bw 384
  ]
  edge [
    source 6
    target 9
    bw 399
    max_bw 399
  ]
  edge [
    source 7
    target 10
    bw 365
    max_bw 365
  ]
  edge [
    source 7
    target 11
    bw 374
    max_bw 374
  ]
  edge [
    source 12
    target 14
    bw 233
    max_bw 233
  ]
  edge [
    source 12
    target 15
    bw 313
    max_bw 313
  ]
  edge [
    source 13
    target 14
    bw 201
    max_bw 201
  ]
  edge [
    source 13
    target 15
    bw 285
    max_bw 285
  ]
  edge [
    source 14
    target 16
    bw 317
    max_bw 317
  ]
  edge [
    source 14
    target 17
    bw 319
    max_bw 319
  ]
  edge [
    source 15
    target 18
    bw 324
    max_bw 324
  ]
  edge [
    source 15
    target 19
    bw 299
    max_bw 299
  ]
  edge [
    source 20
    target 22
    bw 344
    max_bw 344
  ]
  edge [
    source 20
    target 23
    bw 280
    max_bw 280
  ]
  edge [
    source 21
    target 22
    bw 360
    max_bw 360
  ]
  edge [
    source 21
    target 23
    bw 344
    max_bw 344
  ]
  edge [
    source 22
    target 24
    bw 218
    max_bw 218
  ]
  edge [
    source 22
    target 25
    bw 275
    max_bw 275
  ]
  edge [
    source 23
    target 26
    bw 383
    max_bw 383
  ]
  edge [
    source 23
    target 27
    bw 296
    max_bw 296
  ]
  edge [
    source 28
    target 30
    bw 341
    max_bw 341
  ]
  edge [
    source 28
    target 31
    bw 365
    max_bw 365
  ]
  edge [
    source 29
    target 30
    bw 358
    max_bw 358
  ]
  edge [
    source 29
    target 31
    bw 248
    max_bw 248
  ]
  edge [
    source 30
    target 32
    bw 389
    max_bw 389
  ]
  edge [
    source 30
    target 33
    bw 233
    max_bw 233
  ]
  edge [
    source 31
    target 34
    bw 252
    max_bw 252
  ]
  edge [
    source 31
    target 35
    bw 202
    max_bw 202
  ]
]
