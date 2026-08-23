graph [
  node_attrs_setting "_networkx_list_start"
  node_attrs_setting [
    name "cpu"
    type "resource"
    owner "node"
    distribution "uniform"
    dtype "int"
    generative "True"
    low "10"
    high "40"
  ]
  link_attrs_setting "_networkx_list_start"
  link_attrs_setting [
    name "bw"
    type "resource"
    owner "link"
    distribution "uniform"
    dtype "int"
    generative "True"
    low "20"
    high "80"
  ]
  topology___type "random"
  topology___random_prob "0.5"
  output___save_dir "dataset/v_nets"
  output___v_nets_save_dir "v_nets"
  output___v_nets_file_name "v_net.gml"
  output___events_file_name "events.yaml"
  output___setting_file_name "v_sim_setting.yaml"
  id 215
  arrival_time 4262.0
  lifetime 1491.9166496514385
  node [
    id 0
    label "0"
    cpu 16
  ]
  node [
    id 1
    label "1"
    cpu 22
  ]
  node [
    id 2
    label "2"
    cpu 10
  ]
  node [
    id 3
    label "3"
    cpu 27
  ]
  node [
    id 4
    label "4"
    cpu 12
  ]
  node [
    id 5
    label "5"
    cpu 21
  ]
  node [
    id 6
    label "6"
    cpu 22
  ]
  edge [
    source 0
    target 3
    bw 67
  ]
  edge [
    source 0
    target 4
    bw 59
  ]
  edge [
    source 0
    target 5
    bw 41
  ]
  edge [
    source 1
    target 2
    bw 29
  ]
  edge [
    source 1
    target 3
    bw 57
  ]
  edge [
    source 1
    target 6
    bw 51
  ]
  edge [
    source 2
    target 3
    bw 74
  ]
  edge [
    source 2
    target 4
    bw 79
  ]
  edge [
    source 2
    target 5
    bw 61
  ]
  edge [
    source 3
    target 4
    bw 43
  ]
  edge [
    source 3
    target 6
    bw 40
  ]
  edge [
    source 4
    target 5
    bw 46
  ]
  edge [
    source 4
    target 6
    bw 52
  ]
  edge [
    source 5
    target 6
    bw 71
  ]
]
