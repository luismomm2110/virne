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
  id 252
  arrival_time 5034.0
  lifetime 298.5777120479272
  node [
    id 0
    label "0"
    cpu 35
  ]
  node [
    id 1
    label "1"
    cpu 19
  ]
  node [
    id 2
    label "2"
    cpu 18
  ]
  node [
    id 3
    label "3"
    cpu 15
  ]
  node [
    id 4
    label "4"
    cpu 20
  ]
  node [
    id 5
    label "5"
    cpu 33
  ]
  edge [
    source 0
    target 1
    bw 71
  ]
  edge [
    source 0
    target 2
    bw 59
  ]
  edge [
    source 0
    target 3
    bw 45
  ]
  edge [
    source 0
    target 4
    bw 39
  ]
  edge [
    source 0
    target 5
    bw 79
  ]
  edge [
    source 1
    target 4
    bw 52
  ]
  edge [
    source 1
    target 5
    bw 58
  ]
  edge [
    source 2
    target 3
    bw 72
  ]
  edge [
    source 2
    target 5
    bw 37
  ]
  edge [
    source 4
    target 5
    bw 24
  ]
]
