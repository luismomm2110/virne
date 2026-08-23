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
    cpu 94
    max_cpu 94
  ]
  node [
    id 1
    label "1"
    layer "core"
    cpu 97
    max_cpu 97
  ]
  node [
    id 2
    label "2"
    layer "core"
    cpu 50
    max_cpu 50
  ]
  node [
    id 3
    label "3"
    layer "core"
    cpu 53
    max_cpu 53
  ]
  node [
    id 4
    label "4"
    layer "aggregation"
    pod 0
    cpu 53
    max_cpu 53
  ]
  node [
    id 5
    label "5"
    layer "aggregation"
    pod 0
    cpu 89
    max_cpu 89
  ]
  node [
    id 6
    label "6"
    layer "edge"
    pod 0
    cpu 59
    max_cpu 59
  ]
  node [
    id 7
    label "7"
    layer "edge"
    pod 0
    cpu 69
    max_cpu 69
  ]
  node [
    id 8
    label "8"
    layer "host"
    pod 0
    cpu 71
    max_cpu 71
  ]
  node [
    id 9
    label "9"
    layer "host"
    pod 0
    cpu 100
    max_cpu 100
  ]
  node [
    id 10
    label "10"
    layer "host"
    pod 0
    cpu 86
    max_cpu 86
  ]
  node [
    id 11
    label "11"
    layer "host"
    pod 0
    cpu 73
    max_cpu 73
  ]
  node [
    id 12
    label "12"
    layer "aggregation"
    pod 1
    cpu 56
    max_cpu 56
  ]
  node [
    id 13
    label "13"
    layer "aggregation"
    pod 1
    cpu 74
    max_cpu 74
  ]
  node [
    id 14
    label "14"
    layer "edge"
    pod 1
    cpu 74
    max_cpu 74
  ]
  node [
    id 15
    label "15"
    layer "edge"
    pod 1
    cpu 62
    max_cpu 62
  ]
  node [
    id 16
    label "16"
    layer "host"
    pod 1
    cpu 51
    max_cpu 51
  ]
  node [
    id 17
    label "17"
    layer "host"
    pod 1
    cpu 88
    max_cpu 88
  ]
  node [
    id 18
    label "18"
    layer "host"
    pod 1
    cpu 89
    max_cpu 89
  ]
  node [
    id 19
    label "19"
    layer "host"
    pod 1
    cpu 73
    max_cpu 73
  ]
  node [
    id 20
    label "20"
    layer "aggregation"
    pod 2
    cpu 96
    max_cpu 96
  ]
  node [
    id 21
    label "21"
    layer "aggregation"
    pod 2
    cpu 74
    max_cpu 74
  ]
  node [
    id 22
    label "22"
    layer "edge"
    pod 2
    cpu 67
    max_cpu 67
  ]
  node [
    id 23
    label "23"
    layer "edge"
    pod 2
    cpu 87
    max_cpu 87
  ]
  node [
    id 24
    label "24"
    layer "host"
    pod 2
    cpu 75
    max_cpu 75
  ]
  node [
    id 25
    label "25"
    layer "host"
    pod 2
    cpu 63
    max_cpu 63
  ]
  node [
    id 26
    label "26"
    layer "host"
    pod 2
    cpu 58
    max_cpu 58
  ]
  node [
    id 27
    label "27"
    layer "host"
    pod 2
    cpu 59
    max_cpu 59
  ]
  node [
    id 28
    label "28"
    layer "aggregation"
    pod 3
    cpu 70
    max_cpu 70
  ]
  node [
    id 29
    label "29"
    layer "aggregation"
    pod 3
    cpu 66
    max_cpu 66
  ]
  node [
    id 30
    label "30"
    layer "edge"
    pod 3
    cpu 55
    max_cpu 55
  ]
  node [
    id 31
    label "31"
    layer "edge"
    pod 3
    cpu 65
    max_cpu 65
  ]
  node [
    id 32
    label "32"
    layer "host"
    pod 3
    cpu 97
    max_cpu 97
  ]
  node [
    id 33
    label "33"
    layer "host"
    pod 3
    cpu 50
    max_cpu 50
  ]
  node [
    id 34
    label "34"
    layer "host"
    pod 3
    cpu 68
    max_cpu 68
  ]
  node [
    id 35
    label "35"
    layer "host"
    pod 3
    cpu 85
    max_cpu 85
  ]
  edge [
    source 0
    target 4
    bw 377
    max_bw 377
  ]
  edge [
    source 0
    target 12
    bw 229
    max_bw 229
  ]
  edge [
    source 0
    target 20
    bw 347
    max_bw 347
  ]
  edge [
    source 0
    target 28
    bw 347
    max_bw 347
  ]
  edge [
    source 1
    target 4
    bw 342
    max_bw 342
  ]
  edge [
    source 1
    target 12
    bw 367
    max_bw 367
  ]
  edge [
    source 1
    target 20
    bw 232
    max_bw 232
  ]
  edge [
    source 1
    target 28
    bw 393
    max_bw 393
  ]
  edge [
    source 2
    target 5
    bw 209
    max_bw 209
  ]
  edge [
    source 2
    target 13
    bw 385
    max_bw 385
  ]
  edge [
    source 2
    target 21
    bw 327
    max_bw 327
  ]
  edge [
    source 2
    target 29
    bw 232
    max_bw 232
  ]
  edge [
    source 3
    target 5
    bw 231
    max_bw 231
  ]
  edge [
    source 3
    target 13
    bw 351
    max_bw 351
  ]
  edge [
    source 3
    target 21
    bw 363
    max_bw 363
  ]
  edge [
    source 3
    target 29
    bw 314
    max_bw 314
  ]
  edge [
    source 4
    target 6
    bw 383
    max_bw 383
  ]
  edge [
    source 4
    target 7
    bw 228
    max_bw 228
  ]
  edge [
    source 5
    target 6
    bw 234
    max_bw 234
  ]
  edge [
    source 5
    target 7
    bw 328
    max_bw 328
  ]
  edge [
    source 6
    target 8
    bw 328
    max_bw 328
  ]
  edge [
    source 6
    target 9
    bw 364
    max_bw 364
  ]
  edge [
    source 7
    target 10
    bw 253
    max_bw 253
  ]
  edge [
    source 7
    target 11
    bw 333
    max_bw 333
  ]
  edge [
    source 12
    target 14
    bw 238
    max_bw 238
  ]
  edge [
    source 12
    target 15
    bw 217
    max_bw 217
  ]
  edge [
    source 13
    target 14
    bw 279
    max_bw 279
  ]
  edge [
    source 13
    target 15
    bw 332
    max_bw 332
  ]
  edge [
    source 14
    target 16
    bw 305
    max_bw 305
  ]
  edge [
    source 14
    target 17
    bw 242
    max_bw 242
  ]
  edge [
    source 15
    target 18
    bw 386
    max_bw 386
  ]
  edge [
    source 15
    target 19
    bw 231
    max_bw 231
  ]
  edge [
    source 20
    target 22
    bw 320
    max_bw 320
  ]
  edge [
    source 20
    target 23
    bw 201
    max_bw 201
  ]
  edge [
    source 21
    target 22
    bw 265
    max_bw 265
  ]
  edge [
    source 21
    target 23
    bw 369
    max_bw 369
  ]
  edge [
    source 22
    target 24
    bw 257
    max_bw 257
  ]
  edge [
    source 22
    target 25
    bw 235
    max_bw 235
  ]
  edge [
    source 23
    target 26
    bw 302
    max_bw 302
  ]
  edge [
    source 23
    target 27
    bw 319
    max_bw 319
  ]
  edge [
    source 28
    target 30
    bw 211
    max_bw 211
  ]
  edge [
    source 28
    target 31
    bw 374
    max_bw 374
  ]
  edge [
    source 29
    target 30
    bw 282
    max_bw 282
  ]
  edge [
    source 29
    target 31
    bw 291
    max_bw 291
  ]
  edge [
    source 30
    target 32
    bw 328
    max_bw 328
  ]
  edge [
    source 30
    target 33
    bw 342
    max_bw 342
  ]
  edge [
    source 31
    target 34
    bw 299
    max_bw 299
  ]
  edge [
    source 31
    target 35
    bw 253
    max_bw 253
  ]
]
