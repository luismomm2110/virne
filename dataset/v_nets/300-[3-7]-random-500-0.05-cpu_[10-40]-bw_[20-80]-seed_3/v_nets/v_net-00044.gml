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
  id 44
  arrival_time 863.0
  lifetime 270.2661915770329
  node [
    id 0
    label "0"
    cpu 18
  ]
  node [
    id 1
    label "1"
    cpu 18
  ]
  node [
    id 2
    label "2"
    cpu 38
  ]
  node [
    id 3
    label "3"
    cpu 32
  ]
  node [
    id 4
    label "4"
    cpu 19
  ]
  node [
    id 5
    label "5"
    cpu 12
  ]
  node [
    id 6
    label "6"
    cpu 12
  ]
  edge [
    source 0
    target 2
    bw 31
  ]
  edge [
    source 0
    target 3
    bw 36
  ]
  edge [
    source 0
    target 4
    bw 32
  ]
  edge [
    source 0
    target 6
    bw 46
  ]
  edge [
    source 1
    target 2
    bw 53
  ]
  edge [
    source 1
    target 3
    bw 59
  ]
  edge [
    source 1
    target 4
    bw 54
  ]
  edge [
    source 1
    target 5
    bw 53
  ]
  edge [
    source 1
    target 6
    bw 36
  ]
  edge [
    source 2
    target 3
    bw 51
  ]
  edge [
    source 2
    target 4
    bw 69
  ]
  edge [
    source 2
    target 5
    bw 80
  ]
  edge [
    source 2
    target 6
    bw 34
  ]
  edge [
    source 3
    target 4
    bw 57
  ]
  edge [
    source 3
    target 5
    bw 24
  ]
  edge [
    source 3
    target 6
    bw 43
  ]
  edge [
    source 4
    target 5
    bw 73
  ]
  edge [
    source 4
    target 6
    bw 42
  ]
]
