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
  id 49
  arrival_time 978.0
  lifetime 173.3766522279259
  node [
    id 0
    label "0"
    cpu 16
  ]
  node [
    id 1
    label "1"
    cpu 13
  ]
  node [
    id 2
    label "2"
    cpu 38
  ]
  node [
    id 3
    label "3"
    cpu 40
  ]
  node [
    id 4
    label "4"
    cpu 15
  ]
  node [
    id 5
    label "5"
    cpu 34
  ]
  node [
    id 6
    label "6"
    cpu 40
  ]
  edge [
    source 0
    target 2
    bw 61
  ]
  edge [
    source 1
    target 2
    bw 25
  ]
  edge [
    source 1
    target 3
    bw 79
  ]
  edge [
    source 2
    target 5
    bw 36
  ]
  edge [
    source 3
    target 4
    bw 46
  ]
  edge [
    source 3
    target 5
    bw 51
  ]
  edge [
    source 3
    target 6
    bw 26
  ]
  edge [
    source 4
    target 5
    bw 45
  ]
  edge [
    source 4
    target 6
    bw 31
  ]
  edge [
    source 5
    target 6
    bw 37
  ]
]
