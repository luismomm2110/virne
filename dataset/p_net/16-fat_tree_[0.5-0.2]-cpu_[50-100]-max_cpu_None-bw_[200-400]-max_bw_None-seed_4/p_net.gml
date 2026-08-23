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
    cpu 96
    max_cpu 96
  ]
  node [
    id 1
    label "1"
    layer "core"
    cpu 55
    max_cpu 55
  ]
  node [
    id 2
    label "2"
    layer "core"
    cpu 51
    max_cpu 51
  ]
  node [
    id 3
    label "3"
    layer "core"
    cpu 90
    max_cpu 90
  ]
  node [
    id 4
    label "4"
    layer "aggregation"
    pod 0
    cpu 73
    max_cpu 73
  ]
  node [
    id 5
    label "5"
    layer "aggregation"
    pod 0
    cpu 58
    max_cpu 58
  ]
  node [
    id 6
    label "6"
    layer "edge"
    pod 0
    cpu 100
    max_cpu 100
  ]
  node [
    id 7
    label "7"
    layer "edge"
    pod 0
    cpu 59
    max_cpu 59
  ]
  node [
    id 8
    label "8"
    layer "host"
    pod 0
    cpu 89
    max_cpu 89
  ]
  node [
    id 9
    label "9"
    layer "host"
    pod 0
    cpu 95
    max_cpu 95
  ]
  node [
    id 10
    label "10"
    layer "host"
    pod 0
    cpu 80
    max_cpu 80
  ]
  node [
    id 11
    label "11"
    layer "host"
    pod 0
    cpu 90
    max_cpu 90
  ]
  node [
    id 12
    label "12"
    layer "aggregation"
    pod 1
    cpu 86
    max_cpu 86
  ]
  node [
    id 13
    label "13"
    layer "aggregation"
    pod 1
    cpu 100
    max_cpu 100
  ]
  node [
    id 14
    label "14"
    layer "edge"
    pod 1
    cpu 94
    max_cpu 94
  ]
  node [
    id 15
    label "15"
    layer "edge"
    pod 1
    cpu 88
    max_cpu 88
  ]
  node [
    id 16
    label "16"
    layer "host"
    pod 1
    cpu 92
    max_cpu 92
  ]
  node [
    id 17
    label "17"
    layer "host"
    pod 1
    cpu 53
    max_cpu 53
  ]
  node [
    id 18
    label "18"
    layer "host"
    pod 1
    cpu 50
    max_cpu 50
  ]
  node [
    id 19
    label "19"
    layer "host"
    pod 1
    cpu 71
    max_cpu 71
  ]
  node [
    id 20
    label "20"
    layer "aggregation"
    pod 2
    cpu 71
    max_cpu 71
  ]
  node [
    id 21
    label "21"
    layer "aggregation"
    pod 2
    cpu 59
    max_cpu 59
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
    cpu 88
    max_cpu 88
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
    cpu 96
    max_cpu 96
  ]
  node [
    id 26
    label "26"
    layer "host"
    pod 2
    cpu 80
    max_cpu 80
  ]
  node [
    id 27
    label "27"
    layer "host"
    pod 2
    cpu 58
    max_cpu 58
  ]
  node [
    id 28
    label "28"
    layer "aggregation"
    pod 3
    cpu 99
    max_cpu 99
  ]
  node [
    id 29
    label "29"
    layer "aggregation"
    pod 3
    cpu 52
    max_cpu 52
  ]
  node [
    id 30
    label "30"
    layer "edge"
    pod 3
    cpu 73
    max_cpu 73
  ]
  node [
    id 31
    label "31"
    layer "edge"
    pod 3
    cpu 82
    max_cpu 82
  ]
  node [
    id 32
    label "32"
    layer "host"
    pod 3
    cpu 90
    max_cpu 90
  ]
  node [
    id 33
    label "33"
    layer "host"
    pod 3
    cpu 92
    max_cpu 92
  ]
  node [
    id 34
    label "34"
    layer "host"
    pod 3
    cpu 95
    max_cpu 95
  ]
  node [
    id 35
    label "35"
    layer "host"
    pod 3
    cpu 83
    max_cpu 83
  ]
  edge [
    source 0
    target 4
    bw 232
    max_bw 232
  ]
  edge [
    source 0
    target 12
    bw 326
    max_bw 326
  ]
  edge [
    source 0
    target 20
    bw 356
    max_bw 356
  ]
  edge [
    source 0
    target 28
    bw 203
    max_bw 203
  ]
  edge [
    source 1
    target 4
    bw 314
    max_bw 314
  ]
  edge [
    source 1
    target 12
    bw 315
    max_bw 315
  ]
  edge [
    source 1
    target 20
    bw 298
    max_bw 298
  ]
  edge [
    source 1
    target 28
    bw 295
    max_bw 295
  ]
  edge [
    source 2
    target 5
    bw 385
    max_bw 385
  ]
  edge [
    source 2
    target 13
    bw 250
    max_bw 250
  ]
  edge [
    source 2
    target 21
    bw 345
    max_bw 345
  ]
  edge [
    source 2
    target 29
    bw 273
    max_bw 273
  ]
  edge [
    source 3
    target 5
    bw 387
    max_bw 387
  ]
  edge [
    source 3
    target 13
    bw 376
    max_bw 376
  ]
  edge [
    source 3
    target 21
    bw 351
    max_bw 351
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
    bw 222
    max_bw 222
  ]
  edge [
    source 4
    target 7
    bw 395
    max_bw 395
  ]
  edge [
    source 5
    target 6
    bw 390
    max_bw 390
  ]
  edge [
    source 5
    target 7
    bw 390
    max_bw 390
  ]
  edge [
    source 6
    target 8
    bw 275
    max_bw 275
  ]
  edge [
    source 6
    target 9
    bw 223
    max_bw 223
  ]
  edge [
    source 7
    target 10
    bw 256
    max_bw 256
  ]
  edge [
    source 7
    target 11
    bw 314
    max_bw 314
  ]
  edge [
    source 12
    target 14
    bw 398
    max_bw 398
  ]
  edge [
    source 12
    target 15
    bw 399
    max_bw 399
  ]
  edge [
    source 13
    target 14
    bw 383
    max_bw 383
  ]
  edge [
    source 13
    target 15
    bw 381
    max_bw 381
  ]
  edge [
    source 14
    target 16
    bw 285
    max_bw 285
  ]
  edge [
    source 14
    target 17
    bw 279
    max_bw 279
  ]
  edge [
    source 15
    target 18
    bw 236
    max_bw 236
  ]
  edge [
    source 15
    target 19
    bw 259
    max_bw 259
  ]
  edge [
    source 20
    target 22
    bw 307
    max_bw 307
  ]
  edge [
    source 20
    target 23
    bw 251
    max_bw 251
  ]
  edge [
    source 21
    target 22
    bw 208
    max_bw 208
  ]
  edge [
    source 21
    target 23
    bw 365
    max_bw 365
  ]
  edge [
    source 22
    target 24
    bw 272
    max_bw 272
  ]
  edge [
    source 22
    target 25
    bw 387
    max_bw 387
  ]
  edge [
    source 23
    target 26
    bw 325
    max_bw 325
  ]
  edge [
    source 23
    target 27
    bw 254
    max_bw 254
  ]
  edge [
    source 28
    target 30
    bw 296
    max_bw 296
  ]
  edge [
    source 28
    target 31
    bw 358
    max_bw 358
  ]
  edge [
    source 29
    target 30
    bw 332
    max_bw 332
  ]
  edge [
    source 29
    target 31
    bw 254
    max_bw 254
  ]
  edge [
    source 30
    target 32
    bw 275
    max_bw 275
  ]
  edge [
    source 30
    target 33
    bw 208
    max_bw 208
  ]
  edge [
    source 31
    target 34
    bw 231
    max_bw 231
  ]
  edge [
    source 31
    target 35
    bw 240
    max_bw 240
  ]
]
