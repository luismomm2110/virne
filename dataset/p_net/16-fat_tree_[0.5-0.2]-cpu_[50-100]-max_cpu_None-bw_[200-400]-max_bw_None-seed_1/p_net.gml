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
    cpu 87
    max_cpu 87
  ]
  node [
    id 1
    label "1"
    layer "core"
    cpu 93
    max_cpu 93
  ]
  node [
    id 2
    label "2"
    layer "core"
    cpu 62
    max_cpu 62
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
    cpu 59
    max_cpu 59
  ]
  node [
    id 5
    label "5"
    layer "aggregation"
    pod 0
    cpu 61
    max_cpu 61
  ]
  node [
    id 6
    label "6"
    layer "edge"
    pod 0
    cpu 55
    max_cpu 55
  ]
  node [
    id 7
    label "7"
    layer "edge"
    pod 0
    cpu 65
    max_cpu 65
  ]
  node [
    id 8
    label "8"
    layer "host"
    pod 0
    cpu 50
    max_cpu 50
  ]
  node [
    id 9
    label "9"
    layer "host"
    pod 0
    cpu 66
    max_cpu 66
  ]
  node [
    id 10
    label "10"
    layer "host"
    pod 0
    cpu 51
    max_cpu 51
  ]
  node [
    id 11
    label "11"
    layer "host"
    pod 0
    cpu 62
    max_cpu 62
  ]
  node [
    id 12
    label "12"
    layer "aggregation"
    pod 1
    cpu 57
    max_cpu 57
  ]
  node [
    id 13
    label "13"
    layer "aggregation"
    pod 1
    cpu 95
    max_cpu 95
  ]
  node [
    id 14
    label "14"
    layer "edge"
    pod 1
    cpu 56
    max_cpu 56
  ]
  node [
    id 15
    label "15"
    layer "edge"
    pod 1
    cpu 75
    max_cpu 75
  ]
  node [
    id 16
    label "16"
    layer "host"
    pod 1
    cpu 100
    max_cpu 100
  ]
  node [
    id 17
    label "17"
    layer "host"
    pod 1
    cpu 70
    max_cpu 70
  ]
  node [
    id 18
    label "18"
    layer "host"
    pod 1
    cpu 87
    max_cpu 87
  ]
  node [
    id 19
    label "19"
    layer "host"
    pod 1
    cpu 68
    max_cpu 68
  ]
  node [
    id 20
    label "20"
    layer "aggregation"
    pod 2
    cpu 70
    max_cpu 70
  ]
  node [
    id 21
    label "21"
    layer "aggregation"
    pod 2
    cpu 61
    max_cpu 61
  ]
  node [
    id 22
    label "22"
    layer "edge"
    pod 2
    cpu 92
    max_cpu 92
  ]
  node [
    id 23
    label "23"
    layer "edge"
    pod 2
    cpu 78
    max_cpu 78
  ]
  node [
    id 24
    label "24"
    layer "host"
    pod 2
    cpu 79
    max_cpu 79
  ]
  node [
    id 25
    label "25"
    layer "host"
    pod 2
    cpu 64
    max_cpu 64
  ]
  node [
    id 26
    label "26"
    layer "host"
    pod 2
    cpu 100
    max_cpu 100
  ]
  node [
    id 27
    label "27"
    layer "host"
    pod 2
    cpu 54
    max_cpu 54
  ]
  node [
    id 28
    label "28"
    layer "aggregation"
    pod 3
    cpu 73
    max_cpu 73
  ]
  node [
    id 29
    label "29"
    layer "aggregation"
    pod 3
    cpu 73
    max_cpu 73
  ]
  node [
    id 30
    label "30"
    layer "edge"
    pod 3
    cpu 91
    max_cpu 91
  ]
  node [
    id 31
    label "31"
    layer "edge"
    pod 3
    cpu 99
    max_cpu 99
  ]
  node [
    id 32
    label "32"
    layer "host"
    pod 3
    cpu 80
    max_cpu 80
  ]
  node [
    id 33
    label "33"
    layer "host"
    pod 3
    cpu 82
    max_cpu 82
  ]
  node [
    id 34
    label "34"
    layer "host"
    pod 3
    cpu 72
    max_cpu 72
  ]
  node [
    id 35
    label "35"
    layer "host"
    pod 3
    cpu 63
    max_cpu 63
  ]
  edge [
    source 0
    target 4
    bw 337
    max_bw 337
  ]
  edge [
    source 0
    target 12
    bw 207
    max_bw 207
  ]
  edge [
    source 0
    target 20
    bw 263
    max_bw 263
  ]
  edge [
    source 0
    target 28
    bw 261
    max_bw 261
  ]
  edge [
    source 1
    target 4
    bw 222
    max_bw 222
  ]
  edge [
    source 1
    target 12
    bw 257
    max_bw 257
  ]
  edge [
    source 1
    target 20
    bw 201
    max_bw 201
  ]
  edge [
    source 1
    target 28
    bw 328
    max_bw 328
  ]
  edge [
    source 2
    target 5
    bw 260
    max_bw 260
  ]
  edge [
    source 2
    target 13
    bw 208
    max_bw 208
  ]
  edge [
    source 2
    target 21
    bw 341
    max_bw 341
  ]
  edge [
    source 2
    target 29
    bw 315
    max_bw 315
  ]
  edge [
    source 3
    target 5
    bw 375
    max_bw 375
  ]
  edge [
    source 3
    target 13
    bw 321
    max_bw 321
  ]
  edge [
    source 3
    target 21
    bw 400
    max_bw 400
  ]
  edge [
    source 3
    target 29
    bw 230
    max_bw 230
  ]
  edge [
    source 4
    target 6
    bw 271
    max_bw 271
  ]
  edge [
    source 4
    target 7
    bw 331
    max_bw 331
  ]
  edge [
    source 5
    target 6
    bw 398
    max_bw 398
  ]
  edge [
    source 5
    target 7
    bw 349
    max_bw 349
  ]
  edge [
    source 6
    target 8
    bw 249
    max_bw 249
  ]
  edge [
    source 6
    target 9
    bw 257
    max_bw 257
  ]
  edge [
    source 7
    target 10
    bw 203
    max_bw 203
  ]
  edge [
    source 7
    target 11
    bw 396
    max_bw 396
  ]
  edge [
    source 12
    target 14
    bw 224
    max_bw 224
  ]
  edge [
    source 12
    target 15
    bw 243
    max_bw 243
  ]
  edge [
    source 13
    target 14
    bw 276
    max_bw 276
  ]
  edge [
    source 13
    target 15
    bw 226
    max_bw 226
  ]
  edge [
    source 14
    target 16
    bw 252
    max_bw 252
  ]
  edge [
    source 14
    target 17
    bw 280
    max_bw 280
  ]
  edge [
    source 15
    target 18
    bw 309
    max_bw 309
  ]
  edge [
    source 15
    target 19
    bw 315
    max_bw 315
  ]
  edge [
    source 20
    target 22
    bw 241
    max_bw 241
  ]
  edge [
    source 20
    target 23
    bw 215
    max_bw 215
  ]
  edge [
    source 21
    target 22
    bw 264
    max_bw 264
  ]
  edge [
    source 21
    target 23
    bw 396
    max_bw 396
  ]
  edge [
    source 22
    target 24
    bw 225
    max_bw 225
  ]
  edge [
    source 22
    target 25
    bw 311
    max_bw 311
  ]
  edge [
    source 23
    target 26
    bw 335
    max_bw 335
  ]
  edge [
    source 23
    target 27
    bw 226
    max_bw 226
  ]
  edge [
    source 28
    target 30
    bw 353
    max_bw 353
  ]
  edge [
    source 28
    target 31
    bw 304
    max_bw 304
  ]
  edge [
    source 29
    target 30
    bw 222
    max_bw 222
  ]
  edge [
    source 29
    target 31
    bw 209
    max_bw 209
  ]
  edge [
    source 30
    target 32
    bw 395
    max_bw 395
  ]
  edge [
    source 30
    target 33
    bw 326
    max_bw 326
  ]
  edge [
    source 31
    target 34
    bw 223
    max_bw 223
  ]
  edge [
    source 31
    target 35
    bw 325
    max_bw 325
  ]
]
