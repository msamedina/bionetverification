#pragma once

#include <cstdint>
#include <vector>
#include <ostream>

namespace storm {
    namespace abstraction {
        
        class ExplicitGameStrategy {
        public:
            static const uint64_t UNDEFINED;
            
            ExplicitGameStrategy(uint64_t numberOfStates);
            ExplicitGameStrategy(std::vector<uint64_t>&& choices);
            
            uint64_t getNumberOfStates() const;
            uint64_t getChoice(uint64_t state) const;
            void setChoice(uint64_t state, uint64_t choice);
            bool hasDefinedChoice(uint64_t state) const;
            void undefineAll();
            
            uint64_t getNumberOfUndefinedStates() const;
            
        private:
            std::vector<uint64_t> choices;
        };
        
        std::ostream& operator<<(std::ostream& out, ExplicitGameStrategy const& strategy);
        
    }
}
