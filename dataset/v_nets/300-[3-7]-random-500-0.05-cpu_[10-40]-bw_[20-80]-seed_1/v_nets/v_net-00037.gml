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
  id 37
  arrival_time 767.0
  lifetime 543.4206383907914
  node [
    id 0
    label "0"
    cpu 31
  ]
  node [
    id 1
    label "1"
    cpu 35
  ]
  node [
    id 2
    label "2"
    cpu 19
  ]
  node [
    id 3
    label "3"
    cpu 20
  ]
  node [
    id 4
    label "4"
    cpu 16
  ]
  node [
    id 5
    label "5"
    cpu 12
  ]
  edge [
    source 0
    target 1
    bw 50
  ]
  edge [
    source 1
    target 3
    bw 33
  ]
  edge [
    source 1
    target 5
    bw 34
  ]
  edge [
    source 2
    target 5
    bw 47
  ]
  edge [
    source 3
    target 4
    bw 52
  ]
]
