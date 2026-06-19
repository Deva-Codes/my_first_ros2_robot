#include <gz/sim/System.hh>
#include <gz/sim/Model.hh>
#include <gz/sim/components/Joint.hh>
#include <gz/sim/components/JointVelocityCmd.hh>
#include <gz/plugin/Register.hh>
#include <gz/transport/Node.hh>
#include <gz/msgs/twist.pb.h>
#include <iostream>
#include <mutex>
#include <vector>

namespace my_robot
{
    class CustomDrive : public gz::sim::System,
                        public gz::sim::ISystemConfigure,
                        public gz::sim::ISystemPreUpdate
    {
        private:
            gz::transport::Node node;

            gz::sim::Entity left_joint_ent;
            gz::sim::Entity right_joint_ent;

            double target_v = 0.0;
            double target_w = 0.0;

            std::mutex msg_mutex;
            
        public:
        void OnCmdVel(const gz::msgs::Twist &_msg)
        {
            std::lock_guard<std::mutex> lock(msg_mutex);
            target_v = _msg.linear().x();
            target_w = _msg.angular().z();
        }

        void Configure(const gz::sim::Entity &_entity,
                       const std::shared_ptr<const sdf::Element> &_sdf,
                        gz::sim::EntityComponentManager &_ecm,
                        gz::sim::EventManager &_eventMgr) override
        {
            gz::sim::Model model(_entity);
            left_joint_ent = model.JointByName(_ecm, "left_wheel_base");
            right_joint_ent = model.JointByName(_ecm,"right_wheel_base");

            if (left_joint_ent == gz::sim::kNullEntity || right_joint_ent == gz::sim::kNullEntity) {
                std::cerr << "ERROR: Left or Right wheel joint not found! Check URDF names." << std::endl;
            }

            node.Subscribe("/cmd_vel",&CustomDrive::OnCmdVel,this);

            std::cerr << "\n=======================================\n";
            std::cerr <<  "CUSTOM BRAIN ONLINE : Listening for movement commands!\n";
            std::cerr << "=======================================\n" << std::endl;
        }

        void PreUpdate(const gz::sim::UpdateInfo &_info,
                       gz::sim::EntityComponentManager &_ecm) override
        {
            if (_info.paused) return;
            if (left_joint_ent == gz::sim::kNullEntity || right_joint_ent == gz::sim::kNullEntity) return;

            double v,w;
            {
                std::lock_guard<std::mutex> lock(msg_mutex);
                v = target_v;
                w = target_w;
            }
            
            double wheel_separation = 0.64;
            double wheel_radius = 0.2;
            
            // Standard differential drive kinematics
            double v_left =-((v - (w * wheel_separation / 2.0)) / wheel_radius);
            double v_right = -((v + (w * wheel_separation / 2.0)) / wheel_radius);

            // In Gazebo/URDF, positive rotation around Y (axis 0 1 0) 
            // often moves the robot BACKWARD. We negate to move FORWARD.
            std::vector<double> left_cmd = {v_left};
            std::vector<double> right_cmd = {v_right};

            // Apply velocity commands
            if (_ecm.Component<gz::sim::components::JointVelocityCmd>(left_joint_ent) == nullptr) {
                _ecm.CreateComponent(left_joint_ent, gz::sim::components::JointVelocityCmd(left_cmd));
            } else {
                _ecm.SetComponentData<gz::sim::components::JointVelocityCmd>(left_joint_ent, left_cmd);
            }

            if (_ecm.Component<gz::sim::components::JointVelocityCmd>(right_joint_ent) == nullptr) {
                _ecm.CreateComponent(right_joint_ent, gz::sim::components::JointVelocityCmd(right_cmd));
            } else {
                _ecm.SetComponentData<gz::sim::components::JointVelocityCmd>(right_joint_ent, right_cmd);
            }
        }
    };
}

GZ_ADD_PLUGIN(my_robot::CustomDrive,
              gz::sim::System,
              my_robot::CustomDrive::ISystemConfigure,
              my_robot::CustomDrive::ISystemPreUpdate)

GZ_ADD_PLUGIN_ALIAS(my_robot::CustomDrive, "my_robot::CustomDrive")