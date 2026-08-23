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
    high "100"
    low "50"
  ]
  link_attrs_setting [
    name "max_bw"
    type "extrema"
    owner "link"
    originator "bw"
  ]
  topology___num_nodes "32"
  topology___type "tree"
  topology___branching_factor "2"
  topology___wm_alpha "0.5"
  topology___wm_beta "0.2"
  output___save_dir "dataset/p_net"
  output___file_name "tree_p_net.gml"
  node [
    id 0
    label "0"
    layer "switch"
    is_root 1
    cpu 90
    max_cpu 90
  ]
  node [
    id 1
    label "1"
    layer "switch"
    cpu 65
    max_cpu 65
  ]
  node [
    id 2
    label "2"
    layer "switch"
    cpu 95
    max_cpu 95
  ]
  node [
    id 3
    label "3"
    layer "switch"
    cpu 58
    max_cpu 58
  ]
  node [
    id 4
    label "4"
    layer "switch"
    cpu 72
    max_cpu 72
  ]
  node [
    id 5
    label "5"
    layer "switch"
    cpu 93
    max_cpu 93
  ]
  node [
    id 6
    label "6"
    layer "switch"
    cpu 68
    max_cpu 68
  ]
  node [
    id 7
    label "7"
    layer "switch"
    cpu 61
    max_cpu 61
  ]
  node [
    id 8
    label "8"
    layer "switch"
    cpu 90
    max_cpu 90
  ]
  node [
    id 9
    label "9"
    layer "switch"
    cpu 57
    max_cpu 57
  ]
  node [
    id 10
    label "10"
    layer "switch"
    cpu 84
    max_cpu 84
  ]
  node [
    id 11
    label "11"
    layer "switch"
    cpu 99
    max_cpu 99
  ]
  node [
    id 12
    label "12"
    layer "switch"
    cpu 81
    max_cpu 81
  ]
  node [
    id 13
    label "13"
    layer "switch"
    cpu 61
    max_cpu 61
  ]
  node [
    id 14
    label "14"
    layer "switch"
    cpu 71
    max_cpu 71
  ]
  node [
    id 15
    label "15"
    layer "switch"
    cpu 97
    max_cpu 97
  ]
  node [
    id 16
    label "16"
    layer "switch"
    cpu 81
    max_cpu 81
  ]
  node [
    id 17
    label "17"
    layer "switch"
    cpu 76
    max_cpu 76
  ]
  node [
    id 18
    label "18"
    layer "switch"
    cpu 70
    max_cpu 70
  ]
  node [
    id 19
    label "19"
    layer "switch"
    cpu 87
    max_cpu 87
  ]
  node [
    id 20
    label "20"
    layer "switch"
    cpu 89
    max_cpu 89
  ]
  node [
    id 21
    label "21"
    layer "switch"
    cpu 53
    max_cpu 53
  ]
  node [
    id 22
    label "22"
    layer "switch"
    cpu 88
    max_cpu 88
  ]
  node [
    id 23
    label "23"
    layer "switch"
    cpu 54
    max_cpu 54
  ]
  node [
    id 24
    label "24"
    layer "switch"
    cpu 92
    max_cpu 92
  ]
  node [
    id 25
    label "25"
    layer "switch"
    cpu 93
    max_cpu 93
  ]
  node [
    id 26
    label "26"
    layer "switch"
    cpu 89
    max_cpu 89
  ]
  node [
    id 27
    label "27"
    layer "switch"
    cpu 88
    max_cpu 88
  ]
  node [
    id 28
    label "28"
    layer "switch"
    cpu 92
    max_cpu 92
  ]
  node [
    id 29
    label "29"
    layer "switch"
    cpu 83
    max_cpu 83
  ]
  node [
    id 30
    label "30"
    layer "switch"
    cpu 53
    max_cpu 53
  ]
  node [
    id 31
    label "31"
    layer "host"
    cpu 55
    max_cpu 55
  ]
  node [
    id 32
    label "32"
    layer "host"
    cpu 74
    max_cpu 74
  ]
  node [
    id 33
    label "33"
    layer "host"
    cpu 54
    max_cpu 54
  ]
  node [
    id 34
    label "34"
    layer "host"
    cpu 96
    max_cpu 96
  ]
  node [
    id 35
    label "35"
    layer "host"
    cpu 56
    max_cpu 56
  ]
  node [
    id 36
    label "36"
    layer "host"
    cpu 81
    max_cpu 81
  ]
  node [
    id 37
    label "37"
    layer "host"
    cpu 69
    max_cpu 69
  ]
  node [
    id 38
    label "38"
    layer "host"
    cpu 81
    max_cpu 81
  ]
  node [
    id 39
    label "39"
    layer "host"
    cpu 52
    max_cpu 52
  ]
  node [
    id 40
    label "40"
    layer "host"
    cpu 66
    max_cpu 66
  ]
  node [
    id 41
    label "41"
    layer "host"
    cpu 96
    max_cpu 96
  ]
  node [
    id 42
    label "42"
    layer "host"
    cpu 62
    max_cpu 62
  ]
  node [
    id 43
    label "43"
    layer "host"
    cpu 100
    max_cpu 100
  ]
  node [
    id 44
    label "44"
    layer "host"
    cpu 54
    max_cpu 54
  ]
  node [
    id 45
    label "45"
    layer "host"
    cpu 76
    max_cpu 76
  ]
  node [
    id 46
    label "46"
    layer "host"
    cpu 65
    max_cpu 65
  ]
  node [
    id 47
    label "47"
    layer "host"
    cpu 99
    max_cpu 99
  ]
  node [
    id 48
    label "48"
    layer "host"
    cpu 89
    max_cpu 89
  ]
  node [
    id 49
    label "49"
    layer "host"
    cpu 96
    max_cpu 96
  ]
  node [
    id 50
    label "50"
    layer "host"
    cpu 58
    max_cpu 58
  ]
  node [
    id 51
    label "51"
    layer "host"
    cpu 100
    max_cpu 100
  ]
  node [
    id 52
    label "52"
    layer "host"
    cpu 95
    max_cpu 95
  ]
  node [
    id 53
    label "53"
    layer "host"
    cpu 65
    max_cpu 65
  ]
  node [
    id 54
    label "54"
    layer "host"
    cpu 91
    max_cpu 91
  ]
  node [
    id 55
    label "55"
    layer "host"
    cpu 95
    max_cpu 95
  ]
  node [
    id 56
    label "56"
    layer "host"
    cpu 58
    max_cpu 58
  ]
  node [
    id 57
    label "57"
    layer "host"
    cpu 67
    max_cpu 67
  ]
  node [
    id 58
    label "58"
    layer "host"
    cpu 72
    max_cpu 72
  ]
  node [
    id 59
    label "59"
    layer "host"
    cpu 59
    max_cpu 59
  ]
  node [
    id 60
    label "60"
    layer "host"
    cpu 91
    max_cpu 91
  ]
  node [
    id 61
    label "61"
    layer "host"
    cpu 96
    max_cpu 96
  ]
  node [
    id 62
    label "62"
    layer "host"
    cpu 76
    max_cpu 76
  ]
  edge [
    source 0
    target 1
    bw 69
    max_bw 69
  ]
  edge [
    source 0
    target 2
    bw 82
    max_bw 82
  ]
  edge [
    source 1
    target 3
    bw 93
    max_bw 93
  ]
  edge [
    source 1
    target 4
    bw 82
    max_bw 82
  ]
  edge [
    source 2
    target 5
    bw 76
    max_bw 76
  ]
  edge [
    source 2
    target 6
    bw 100
    max_bw 100
  ]
  edge [
    source 3
    target 7
    bw 58
    max_bw 58
  ]
  edge [
    source 3
    target 8
    bw 62
    max_bw 62
  ]
  edge [
    source 4
    target 9
    bw 60
    max_bw 60
  ]
  edge [
    source 4
    target 10
    bw 90
    max_bw 90
  ]
  edge [
    source 5
    target 11
    bw 84
    max_bw 84
  ]
  edge [
    source 5
    target 12
    bw 59
    max_bw 59
  ]
  edge [
    source 6
    target 13
    bw 87
    max_bw 87
  ]
  edge [
    source 6
    target 14
    bw 56
    max_bw 56
  ]
  edge [
    source 7
    target 15
    bw 72
    max_bw 72
  ]
  edge [
    source 7
    target 16
    bw 56
    max_bw 56
  ]
  edge [
    source 8
    target 17
    bw 69
    max_bw 69
  ]
  edge [
    source 8
    target 18
    bw 68
    max_bw 68
  ]
  edge [
    source 9
    target 19
    bw 51
    max_bw 51
  ]
  edge [
    source 9
    target 20
    bw 54
    max_bw 54
  ]
  edge [
    source 10
    target 21
    bw 90
    max_bw 90
  ]
  edge [
    source 10
    target 22
    bw 67
    max_bw 67
  ]
  edge [
    source 11
    target 23
    bw 56
    max_bw 56
  ]
  edge [
    source 11
    target 24
    bw 87
    max_bw 87
  ]
  edge [
    source 12
    target 25
    bw 83
    max_bw 83
  ]
  edge [
    source 12
    target 26
    bw 68
    max_bw 68
  ]
  edge [
    source 13
    target 27
    bw 70
    max_bw 70
  ]
  edge [
    source 13
    target 28
    bw 76
    max_bw 76
  ]
  edge [
    source 14
    target 29
    bw 73
    max_bw 73
  ]
  edge [
    source 14
    target 30
    bw 72
    max_bw 72
  ]
  edge [
    source 15
    target 31
    bw 93
    max_bw 93
  ]
  edge [
    source 15
    target 47
    bw 87
    max_bw 87
  ]
  edge [
    source 16
    target 32
    bw 60
    max_bw 60
  ]
  edge [
    source 16
    target 48
    bw 58
    max_bw 58
  ]
  edge [
    source 17
    target 33
    bw 76
    max_bw 76
  ]
  edge [
    source 17
    target 49
    bw 85
    max_bw 85
  ]
  edge [
    source 18
    target 34
    bw 77
    max_bw 77
  ]
  edge [
    source 18
    target 50
    bw 82
    max_bw 82
  ]
  edge [
    source 19
    target 35
    bw 66
    max_bw 66
  ]
  edge [
    source 19
    target 51
    bw 71
    max_bw 71
  ]
  edge [
    source 20
    target 36
    bw 93
    max_bw 93
  ]
  edge [
    source 20
    target 52
    bw 79
    max_bw 79
  ]
  edge [
    source 21
    target 37
    bw 66
    max_bw 66
  ]
  edge [
    source 21
    target 53
    bw 90
    max_bw 90
  ]
  edge [
    source 22
    target 38
    bw 56
    max_bw 56
  ]
  edge [
    source 22
    target 54
    bw 60
    max_bw 60
  ]
  edge [
    source 23
    target 39
    bw 87
    max_bw 87
  ]
  edge [
    source 23
    target 55
    bw 67
    max_bw 67
  ]
  edge [
    source 24
    target 40
    bw 65
    max_bw 65
  ]
  edge [
    source 24
    target 56
    bw 80
    max_bw 80
  ]
  edge [
    source 25
    target 41
    bw 63
    max_bw 63
  ]
  edge [
    source 25
    target 57
    bw 76
    max_bw 76
  ]
  edge [
    source 26
    target 42
    bw 89
    max_bw 89
  ]
  edge [
    source 26
    target 58
    bw 93
    max_bw 93
  ]
  edge [
    source 27
    target 43
    bw 97
    max_bw 97
  ]
  edge [
    source 27
    target 59
    bw 70
    max_bw 70
  ]
  edge [
    source 28
    target 44
    bw 72
    max_bw 72
  ]
  edge [
    source 28
    target 60
    bw 99
    max_bw 99
  ]
  edge [
    source 29
    target 45
    bw 86
    max_bw 86
  ]
  edge [
    source 29
    target 61
    bw 77
    max_bw 77
  ]
  edge [
    source 30
    target 46
    bw 50
    max_bw 50
  ]
  edge [
    source 30
    target 62
    bw 90
    max_bw 90
  ]
]
